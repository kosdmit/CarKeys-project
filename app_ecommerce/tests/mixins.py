import pytest
from mixer.backend.django import mixer

from app_ecommerce.models import Category, Goods, Service
from app_ecommerce.tests.data import TEST_DATA


class CreateTestObjectsMixin:
    @pytest.fixture()
    def prepare_goods(self, request):
        self.top_level_categories = mixer.cycle(5).blend(Category, parent=None)
        self.second_level_categories = [mixer.cycle(3).blend(Category, parent=cat) for cat in self.top_level_categories]

        self.available_goods = mixer.cycle(10).blend(Goods, parent=mixer.select, is_active=True, count=1)
        self.unavailable_goods = mixer.cycle(2).blend(Goods, parent=mixer.select, is_active=True, count=0)
        self.disabled_goods = mixer.blend(Goods, parent=mixer.select, is_active=False)

        self.selected_top_level_category = mixer.blend(Category, parent=None, title=TEST_DATA['top_level_category_title'])
        self.top_level_categories.append(self.selected_top_level_category)

    @pytest.fixture()
    def prepare_services(self, request):
        self.active_services = mixer.cycle(3).blend(Service, is_active=True)
        self.disabled_services = mixer.blend(Service, is_active=False)