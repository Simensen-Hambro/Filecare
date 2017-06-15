from django.contrib import admin

from portal.models import SharedNode, Node


class SharedNodeAdmin(admin.ModelAdmin):
    actions = ['really_delete_selected']

    def get_actions(self, request):
        actions = super(SharedNodeAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 share entry was"
        else:
            message_bit = "%s shares entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)

    really_delete_selected.short_description = "Delete selected entries"


admin.site.register(SharedNode, SharedNodeAdmin)
admin.site.register(Node)
