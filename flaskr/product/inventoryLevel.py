import graphene
from inventoryItem import InventoryItem


class InventoryQuantity(graphene.ObjectType):
    name = graphene.String(
        required=True,
        description="Name of the quantity type (e.g., 'available', 'incoming')."
    )
    quantity = graphene.Int(required=True, description="The quantity amount.")


class Location(graphene.ObjectType):
    # 假设包含Location的基本字段，这里简化表示
    id = graphene.ID(required=True)
    name = graphene.String(description="The name of the location.")


class InventoryLevel(graphene.ObjectType):

    canDeactivate = graphene.Boolean(
        required=True,
        description="Whether the inventory level can be deactivated.")
    createdAt = graphene.DateTime(
        required=True,
        description="The date and time when the inventory level was created.")
    deactivationAlert = graphene.String(
        description=
        "Describes either the impact of deactivating the inventory level, or why it can't be deactivated."
    )
    id = graphene.ID(required=True, description="A globally-unique ID.")
    item = graphene.Field(
        InventoryItem,
        required=True,
        description="Inventory item associated with the inventory level.")
    location = graphene.Field(
        Location,
        required=True,
        description="The location associated with the inventory level.")
    quantities = graphene.List(
        InventoryQuantity,
        required=True,
        description="Quantities for the requested names.")
    updatedAt = graphene.DateTime(
        required=True,
        description="The date and time when the inventory level was updated.")
