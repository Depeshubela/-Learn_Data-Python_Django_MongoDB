from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


#定義書籍類型(如科幻小說、愛情小說、參考書.....)
class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')
    def __str__(self):
        return self.name
        
#紀錄書本資料(名稱、作者、ISBN等)
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True) #on_delete:刪除時的反應，如顯示確認訊息 此為null
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

    def __str__(self):
        return self.title


    #回傳一個存取此資料的url給html，此處用於book_list.html
    def get_absolute_url(self):
        #book-detail對應catalog/urls.py裡的urlpatterns，後方args為reverse必要參數(id)
        #reverse實現動態網址，urls.py改變即可變全部
        return reverse('book-detail', args=[str(self.id)]) 

    #多對多沒辦法直接filter需要另外創建
    def display_genre(self):
        #print((genre.name for genre in self.genre.all()).__next__())
        return ', '.join(genre.name for genre in self.genre.all()[:3]) #用join取genre編譯器資料

    display_genre.short_description = 'Genre' #short_description:管理者網站中出現的標題



#書本外在訊息(是否在館、版本說明等)
class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True) #null:允許寫入null(char則為空字串) blank:允許為空白
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property #驗證圖書是否逾期未還
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back: #due_back(還書日期)不可為空
            return True
        return False

    LOAN_STATUS = (
        ('m', '維護'),
        ('o', '外借'),
        ('a', '可用'),
        ('r', '已預定'),
    )

    status = models.CharField(max_length=1,choices=LOAN_STATUS,blank=True,default='m',help_text='Book availability')

    class Meta: #meta 類似補充信息?
        ordering = ['due_back'] #ordering:升冪排列 前面加-為降冪排列

        #在後臺新增一個新的權限叫can_.....可在後續自由調用用以測試是否符合權限(記得先到後台給權限)

        permissions = (("can_mark_returned", "Set book as returned"),) 
    def __str__(self):
        return f'{self.id} ({self.book.title})' 


#作者資料
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name'] #先last升冪再first升冪 

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)
