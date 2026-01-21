import logging
from typing import Any


from commons.typed_config.standard_field_converters import FieldConverter, ConversionContext, DataclassFieldConverter, \
    PathFieldConverter, TrivialFieldConverter, ListFieldConverter, DictFieldConverter, DatetimeFieldConverter, \
    EnumFieldConverter
from commons.util.singleton import Singleton

log = logging.getLogger(__name__)

class ConverterRegistry(metaclass=Singleton):
    def __init__(self):
        self._converters: set[FieldConverter] = set()

        self.register(DataclassFieldConverter)
        self.register(PathFieldConverter)
        self.register(DictFieldConverter)
        self.register(ListFieldConverter)
        self.register(TrivialFieldConverter)
        self.register(DatetimeFieldConverter)
        self.register(EnumFieldConverter)

    def register(
            self,
            converter: FieldConverter | type[FieldConverter]
    ) -> None:
        if isinstance(converter, type):
            if not issubclass(converter, FieldConverter):
                raise TypeError("Expected the 'converter' parameter to be a subclass of 'FieldConverter'.")
            else:
                converter = converter()

        self._converters.add(converter)

    def __call__[T](
            self,
            value: Any,
            context: ConversionContext[T]
    ) -> T:
        type_ = context.target_type

        for converter in self._converters:
            try:
                conversion_possible = converter.accepts_target_type(type_)
            except BaseException as e:
                logging.warning(e)
                conversion_possible = False

            if conversion_possible:
                result = converter(value, context)
                break

        else:
            result = value

            message = f"file='{context.source_file}' field={context.canonical_field_name} target_type={type_} message='No requested type conversion found!'"
            if context.strict:
                raise ValueError(message)
            else:
                log.warning(message)

        return result
