from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView


# Create your views here.
class MainView(TemplateView):
    template_name = 'app_landing/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['goods_link'] = reverse_lazy('goods')

        return context

