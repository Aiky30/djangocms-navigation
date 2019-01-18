from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import View

from cms.models import Page

from djangocms_navigation.utils import is_model_supported, supported_models


class ContentObjectSelect2View(View):
    def get(self, request, *args, **kwargs):

        content_type_id = self.request.GET.get("content_type_id", None)
        # Return http bad request if there is no content_type_id provided in request
        if not content_type_id:
            return HttpResponseBadRequest()

        # return http bad request if content_type not exist in db
        try:
            content_object = ContentType.objects.get_for_id(content_type_id)
        except ContentType.DoesNotExist:
            return HttpResponseBadRequest()

        # return http bad request if content type is not registered to use navigation app
        model = content_object.model_class()
        if not is_model_supported(model):
            return HttpResponseBadRequest()

        self.site = get_current_site(request)

        data = {
            "results": [{"text": str(obj), "id": obj.pk} for obj in self.get_data()]
        }
        return JsonResponse(data)

    def get_data(self):
        content_type_id = self.request.GET.get("content_type_id", None)
        query = self.request.GET.get("query", None)
        site = self.request.GET.get("site")
        content_object = ContentType.objects.get_for_id(content_type_id)
        model = content_object.model_class()

        try:
            # If versioning is enabled then get versioning queryset for model
            app_config = apps.get_app_config("djangocms_versioning")
            versionable_item = app_config.cms_extension.versionables_by_grouper[model]
            queryset = versionable_item.grouper_choices_queryset()
        except (LookupError, KeyError):
            queryset = model.objects.all()

        try:
            pk = int(self.request.GET.get("pk"))
        except (TypeError, ValueError):
            pk = None

        if site:
            if hasattr(model.objects, "on_site"):
                queryset = queryset.on_site(site)
            elif hasattr(model, "site"):
                queryset = queryset.filter(site=site)

        if pk:
            queryset = queryset.filter(pk=pk)

        if query:
            # For Page model loop through all title objects to exclude the
            # object which doesnt match query
            if model == Page:
                # Todo: Improve filtering using title_set instead of in python
                for item in queryset:
                    if item.get_page_title().lower().find(query.lower()) == -1:
                        queryset = queryset.exclude(pk=item.pk)
            else:
                # Non page model should work using filter against field in queryset
                options = {}
                search_fields = supported_models().get(model)
                if search_fields:
                    for field in search_fields:
                        options[field] = query
                    queryset = queryset.filter(**options)

        return queryset

    def get_paginate_by(self, queryset):
        return self.request.GET.get("limit", 30)
