import sqlalchemy as sa


def get_class_by_tablename(base, tablename, data=None):
    found_classes = set(
        c for c in base._decl_class_registry.values()
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename
    )
    if len(found_classes) > 1:
        if not data:
            raise ValueError(
                "Multiple declarative classes found for table '{0}'. "
                "Please provide data parameter for this function to be able "
                "to determine polymorphic scenarios.".format(
                    tablename
                )
            )
        else:
            for cls in found_classes:
                mapper = sa.inspect(cls)
                polymorphic_on = mapper.polymorphic_on.name
                if polymorphic_on in data:
                    if data[polymorphic_on] == mapper.polymorphic_identity:
                        return cls
            raise ValueError(
                "Multiple declarative classes found for table '{0}'. Given "
                "data row does not match any polymorphic identity of the "
                "found classes.".format(
                    tablename
                )
            )
    elif found_classes:
        return found_classes.pop()
    return None
