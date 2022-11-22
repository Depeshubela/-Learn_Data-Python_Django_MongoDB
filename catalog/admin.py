from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)

#@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death') #author的列表名稱
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]#新增author的排列順序 ()內為水平放置
admin.site.register(Author, AuthorAdmin)

#將下方BookInstance與新增Book介面連接
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


@admin.register(Book) #此行寫法等同於admin.site.register()
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    #與bookinstance連接
    inlines = [BooksInstanceInline] 
#admin.site.register(Book, BookAdmin)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back') #右方目錄列

    #將新增頁面分類
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')
        }),
    )
