from commons.terrarium.component.descriptor import ComponentDescriptor
from commons.terrarium.component.proxy import ComponentProxy


class ComponentDescriptorFactory:
    @staticmethod
    def full(component_proxy: ComponentProxy) -> ComponentDescriptor:
        return ComponentDescriptor(
            type_=component_proxy.type_,
            name=component_proxy.name
        )

    @staticmethod
    def of(*, type_: type = None, name: str = None) -> ComponentDescriptor:
        return ComponentDescriptor(
            type_=type_,
            name=name
        )
