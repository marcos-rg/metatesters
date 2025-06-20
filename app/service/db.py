from typing import Type, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import json
import uuid

# SQLAlchemy setup
Base = declarative_base()
T = TypeVar('T', bound=BaseModel)

class SQLiteService:
    def __init__(self, db_path: str = "local_db.sqlite"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.tables = {}  # Store table classes by model name
        
    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
        
    def create_table_for_model(self, model_class: Type[BaseModel]) -> Type:
        """Dynamically create SQLAlchemy table for Pydantic model"""
        table_name = model_class.__name__.lower()
        
        if table_name in self.tables:
            return self.tables[table_name]
        
        # Get model fields
        fields = model_class.model_fields
        
        # Create table attributes
        attrs = {
            '__tablename__': table_name,
            'id': Column(String, primary_key=True),
        }
        
        # Add columns for each field
        for field_name, field_info in fields.items():
            if field_name == 'id':
                continue
                
            # Check if field is another Pydantic model (nested)
            field_type = field_info.annotation
            if hasattr(field_type, 'model_fields'):  # It's a Pydantic model
                # Add foreign key column
                attrs[f'{field_name}_id'] = Column(String, ForeignKey(f'{field_type.__name__.lower()}.id'))
                # Create the nested table if it doesn't exist
                nested_table = self.create_table_for_model(field_type)
                # Add relationship
                attrs[field_name] = relationship(nested_table.__name__)
            else:
                # Regular field - store as JSON text for complex types
                attrs[field_name] = Column(Text)
        
        # Create the table class
        table_class = type(f'{model_class.__name__}Table', (Base,), attrs)
        self.tables[table_name] = table_class
        
        return table_class
    
    def ensure_tables_exist(self):
        """Create only tables that don't exist in the database"""
        # Get all table names that need to be created
        tables_to_create = []
        for table_name, table_class in self.tables.items():
            if not self._table_exists(table_name):
                tables_to_create.append(table_class)
        
        # Only create tables that don't exist
        if tables_to_create:
            for table_class in tables_to_create:
                table_class.__table__.create(bind=self.engine, checkfirst=True)
    
    def _get_session(self) -> Session:
        return self.SessionLocal()
    
    def _pydantic_to_dict(self, obj: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic object to dict, handling nested objects"""
        result = {}
        
        # Handle the id field specially - check if it exists as a property
        if hasattr(obj, 'id'):
            result['id'] = obj.id
        
        for field_name, value in obj.model_dump().items():
            if field_name != 'id':  # Skip id if it's already handled above
                if isinstance(value, (dict, list)):
                    # Store complex types as JSON
                    result[field_name] = json.dumps(value)
                else:
                    result[field_name] = value
        return result
    
    def _dict_to_pydantic(self, data: Dict[str, Any], model_class: Type[T], session: Session) -> T:
        """Convert dict back to Pydantic object, handling nested objects"""
        result_data = {}
        
        for field_name, field_info in model_class.model_fields.items():
            if field_name == 'id':
                result_data[field_name] = data.get('id')
                continue
                
            field_type = field_info.annotation
            
            if hasattr(field_type, 'model_fields'):  # Nested Pydantic model
                nested_id = data.get(f'{field_name}_id')
                if nested_id:
                    nested_obj = self.read(nested_id, field_type, session=session)
                    result_data[field_name] = nested_obj
            else:
                value = data.get(field_name)
                if isinstance(value, str) and field_name not in ['id']:
                    try:
                        # Try to parse as JSON for complex types
                        result_data[field_name] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result_data[field_name] = value
                else:
                    result_data[field_name] = value
        
        return model_class(**result_data)
    
    def create(self, obj: T) -> T:
        """Create a new record"""
        session = self._get_session()
        try:
            model_class = obj.__class__
            table_class = self.create_table_for_model(model_class)
            self.ensure_tables_exist()
            
            # Handle nested objects first
            for field_name, field_info in model_class.model_fields.items():
                field_type = field_info.annotation
                if hasattr(field_type, 'model_fields'):  # Nested Pydantic model
                    nested_obj = getattr(obj, field_name, None)
                    if nested_obj:
                        # Check if nested object exists, create if not
                        existing = session.query(self.create_table_for_model(field_type)).filter_by(id=nested_obj.id).first()
                        if not existing:
                            self.create(nested_obj)
            
            # Convert to dict and create record
            data = self._pydantic_to_dict(obj)
            db_obj = table_class(**data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            
            return obj
        finally:
            session.close()
    
    def read(self, obj_id: str, model_class: Type[T], session: Optional[Session] = None) -> Optional[T]:
        """Read a record by ID"""
        should_close = session is None
        if session is None:
            session = self._get_session()
        
        try:
            table_class = self.create_table_for_model(model_class)
            self.ensure_tables_exist()
            
            db_obj = session.query(table_class).filter_by(id=obj_id).first()
            if not db_obj:
                return None
            
            # Convert back to dict
            data = {c.name: getattr(db_obj, c.name) for c in table_class.__table__.columns}
            
            return self._dict_to_pydantic(data, model_class, session)
        finally:
            if should_close:
                session.close()
    
    def read_all(self, model_class: Type[T], session: Optional[Session] = None) -> List[T]:
        """Read all records of a given model type"""
        should_close = session is None
        if session is None:
            session = self._get_session()
        
        try:
            table_class = self.create_table_for_model(model_class)
            self.ensure_tables_exist()
            
            db_objs = session.query(table_class).all()
            
            result = []
            for db_obj in db_objs:
                # Convert back to dict
                data = {c.name: getattr(db_obj, c.name) for c in table_class.__table__.columns}
                pydantic_obj = self._dict_to_pydantic(data, model_class, session)
                result.append(pydantic_obj)
            
            return result
        finally:
            if should_close:
                session.close()

    def update(self, obj: T) -> Optional[T]:
        """Update an existing record"""
        session = self._get_session()
        try:
            model_class = obj.__class__
            table_class = self.create_table_for_model(model_class)
            self.ensure_tables_exist()
            
            # Handle nested objects first
            for field_name, field_info in model_class.model_fields.items():
                field_type = field_info.annotation
                if hasattr(field_type, 'model_fields'):  # Nested Pydantic model
                    nested_obj = getattr(obj, field_name, None)
                    if nested_obj:
                        existing = session.query(self.create_table_for_model(field_type)).filter_by(id=nested_obj.id).first()
                        if not existing:
                            self.create(nested_obj)
                        else:
                            self.update(nested_obj)
            
            # Update the main record
            data = self._pydantic_to_dict(obj)
            session.query(table_class).filter_by(id=obj.id).update(data)
            session.commit()
            
            return obj
        finally:
            session.close()
    
    def delete(self, obj_id: str, model_class: Type[T]) -> bool:
        """Delete a record by ID"""
        session = self._get_session()
        try:
            table_class = self.create_table_for_model(model_class)
            self.ensure_tables_exist()
            
            result = session.query(table_class).filter_by(id=obj_id).delete()
            session.commit()
            
            return result > 0
        finally:
            session.close()


if __name__ == "__main__":

    # Example Pydantic models for testing
    class Address(BaseModel):
        id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        street: str
        city: str
        country: str

    class Person(BaseModel):
        id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        name: str
        age: int
        address: Address

    # Test the SQLite service
    service = SQLiteService("test_db.sqlite")
    
    # Create test objects
    address = Address(street="123 Main St", city="New York", country="USA")
    person = Person(name="John Doe", age=10, address=address)

    address2 = Address(street="456 Elm St", city="San Francisco", country="USA")
    person2 = Person(name="daniel", age=30, address=address2)

    print("Original person:", person)
    print("Original address:", address)
    
    # Test CREATE
    print("\n--- Testing CREATE ---")
    created_person = service.create(person)
    created_person2 = service.create(person2)
    print("Created person2:", created_person2)
    print("Created person:", created_person)
    
    # Test READ
    print("\n--- Testing READ ---")
    read_person = service.read(person.id, Person)
    print("Read person:", read_person)
    print("Address from read person:", read_person.address if read_person else None)

    # Test READ ALL
    print("\n--- Testing READ ALL people ---")
    all_people = service.read_all(Person)
    print("All people:", all_people)

    # Test READ ALL
    print("\n--- Testing READ ALL addresses ---")
    all_addresses = service.read_all(Address)
    print("All addresses:", all_addresses)

    # Test UPDATE
    print("\n--- Testing UPDATE ---")
    if read_person:
        read_person.age = 31
        read_person.address.city = "Medellín"
        updated_person = service.update(read_person)
        print("Updated person:", updated_person)
        
        # Verify update
        verify_person = service.read(person.id, Person)
        print("Verified updated person:", verify_person)
    
    # Test DELETE
    print("\n--- Testing DELETE ---")
    deleted = service.delete(person.id, Person)
    print("Deleted:", deleted)
    
    # Verify deletion
    verify_deleted = service.read(person.id, Person)
    print("Person after deletion:", verify_deleted)
    
    # Address should still exist (no cascade delete implemented)
    verify_address = service.read(address.id, Address)
    print("Address after person deletion:", verify_address)