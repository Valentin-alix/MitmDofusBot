from PyQt5.QtWidgets import QLabel, QTableWidgetItem
from sqlalchemy import Engine, func, case
from sqlalchemy.orm import sessionmaker

from app.database.models import CategoryEnum, Item, Price, Ingredient, Recipe, TypeItem
from app.gui.components.common import Widget, TableWidget
from app.gui.components.organization import VerticalLayout


class BenefitRecipeTable(Widget):
    def __init__(self, engine: Engine):
        super().__init__()
        self.engine = engine
        self.server_id: int | None
        v_layout = VerticalLayout()
        self.setLayout(v_layout)

        title = QLabel(parent=self, text="Meilleur bénéfice sur les crafts")
        v_layout.addWidget(title)

        table_benefit_recipe_scroll = TableWidget(["Nom", "Bénéfice"])
        self.table_benefit_recipe = table_benefit_recipe_scroll.table
        v_layout.addWidget(table_benefit_recipe_scroll)

    def get_benefit_recipe(self):
        self.table_benefit_recipe.clearContents()
        self.table_benefit_recipe.setRowCount(0)

        rows = 40

        benefit_recipe = get_benefit_from_craft(self.engine, self.server_id)

        self.table_benefit_recipe.setRowCount(rows)
        for index, (name, benefit) in enumerate(benefit_recipe):
            name_col = QTableWidgetItem(name)
            benefit_col = QTableWidgetItem(str(benefit))

            self.table_benefit_recipe.setItem(index, 0, name_col)
            self.table_benefit_recipe.setItem(index, 1, benefit_col)


def get_benefit_from_craft(engine: Engine, server_id: int | None, category: CategoryEnum = CategoryEnum.EQUIPMENT,
                           type_item: str | None = None, limit=40):
    # TODO FILTER TO GET RECIPE WITH ALL INGREDIENTS NOT WORKING
    with sessionmaker(bind=engine)() as session:
        _items_latest_date = (
            session.query(
                Item.id,
                func.max(Price.creation_date).label("latest_date")
            )
            .join(Price, Price.item_id == Item.id)
            .filter(Price.server_id == server_id)
            .group_by(Item.id)
            .subquery()
        )

        _price_latest_date = (
            session.query(
                Item.id,
                Price.one
            )
            .join(Price, Price.item_id == Item.id).join(
                _items_latest_date, _items_latest_date.c.id == Item.id
            )
            .filter(Price.creation_date == _items_latest_date.c.latest_date)
            .subquery()
        )

        return session.query(Ingredient.id).join(
            _price_latest_date,
            _price_latest_date.c.id == Ingredient.item_id).join(
            Recipe,
            Recipe.id == Ingredient.recipe_id).join(Price, Price.item_id == Recipe.result_item_id).join(Item,
                                                                                                        Item.id == Recipe.result_item_id).join(
            TypeItem, TypeItem.id == Item.type_item_id).group_by(
            Ingredient.recipe_id).having(
            TypeItem.category == category,
            Price.server_id == server_id,
            (func.sum(case((_price_latest_date.c.one == 0, 1), else_=0)) == 0)).order_by(
            func.sum(_price_latest_date.c.one * Ingredient.quantity) - Price.one).with_entities(
            Item.name,
            Price.one - func.sum(_price_latest_date.c.one * Ingredient.quantity)).limit(limit)
