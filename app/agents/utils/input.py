from langchain_core.messages import (AIMessage, ChatMessage, FunctionMessage,
                                     HumanMessage, SystemMessage, ToolMessage)
from typing import (Any, Dict, List, Set, Tuple, Type,
                    Union)

class TypeAnnotator:
    _iterables = [list, tuple, set, dict]
    _message_types = [HumanMessage, AIMessage, ToolMessage, SystemMessage,
                     FunctionMessage, ChatMessage]
    _no_iterables = [int, float, str, bool] + _message_types

    def __init__(self, obj: Any):
        self.obj = obj

    def get_type(self) -> Type:
        """Get the type annotation directly as a typing object."""
        return self._infer_type(self.obj)

    def _infer_type(self, obj: Any) -> Type:
        """Recursively determine the type annotation of a complex structure."""
        # Handle message types first
        if any(isinstance(obj, t) for t in self._message_types):
            return type(obj)

        # Handle basic types
        if type(obj) in self._no_iterables:
            return type(obj)

        # Handle collections
        handlers = {
            list: self._handle_list,
            dict: self._handle_dict,
            tuple: self._handle_tuple,
            set: self._handle_set
        }
        return handlers.get(type(obj), lambda x: type(x))(obj)

    def _handle_list(self, obj: List) -> Type[List]:
        """Handle list type annotation."""
        if not obj:
            return List[Any]

        types = {self._infer_type(el) for el in obj}
        if len(types) == 1:
            return List[next(iter(types))]
        return List[Union[tuple(sorted(types, key=str))]]

    def _handle_dict(self, obj: Dict) -> Type[Dict]:
        """Handle dict type annotation."""
        if not obj:
            return Dict[Any, Any]

        key_types = {self._infer_type(k) for k in obj.keys()}
        value_types = {self._infer_type(v) for v in obj.values()}

        key_type = (Union[tuple(sorted(key_types, key=str))]
                   if len(key_types) > 1 else next(iter(key_types)))
        value_type = (Union[tuple(sorted(value_types, key=str))]
                     if len(value_types) > 1 else next(iter(value_types)))

        return Dict[key_type, value_type]

    def _handle_tuple(self, obj: Tuple) -> Type[Tuple]:
        """Handle tuple type annotation."""
        if not obj:
            return Tuple[()]
        return Tuple[tuple(self._infer_type(el) for el in obj)]

    def _handle_set(self, obj: Set) -> Type[Set]:
        """Handle set type annotation."""
        if not obj:
            return Set[Any]

        types = {self._infer_type(el) for el in obj}
        if len(types) == 1:
            return Set[next(iter(types))]
        return Set[Union[tuple(sorted(types, key=str))]]
