import pytest
from mixer.backend.django import mixer

from app_ecommerce.models import Category, Goods, Service, Parameter


@pytest.mark.django_db
class TestBaseModel:
    @pytest.mark.parametrize("obj_class", [Goods, Category, Service])
    def test_save_method(self, obj_class):
        obj_list = mixer.cycle(5).blend(obj_class, num_id=None)
        second_obj_list = mixer.cycle(5).blend(Parameter, num_id=None)

        num_id_set = set()
        for obj in obj_list:
            num_id_set.add(obj.num_id)

        second_num_id_set = set()
        for obj in second_obj_list:
            second_num_id_set.add(obj.num_id)

        assert len(num_id_set) == 5
        assert all(num in num_id_set for num in [1, 2, 3, 4, 5])
        assert num_id_set == second_num_id_set
