from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "product",
        "rating",
        "short_comment",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
        "product",
    )

    search_fields = (
        "user__username",
        "product__name",
        "comment",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    def short_comment(self, obj):
        if obj.comment:
            return obj.comment[:40] + "..." if len(obj.comment) > 40 else obj.comment
        return "-"
    short_comment.short_description = "Comment"