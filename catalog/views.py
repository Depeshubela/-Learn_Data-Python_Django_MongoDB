from django.http import Http404
from django.shortcuts import render 
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin 
from .models import Author, Book, BookInstance
from django.contrib.auth.decorators import permission_required
from .forms import RenewBookForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
#from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory


def index(request):
    num_books = Book.objects.all().count() #計算book總數 下同
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    #訪問次數
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    #將上述計算結果存入context待下述丟入html


    #test button
    if 'ok' in request.POST: 
        request.session.flush()
        num_visits = request.session.get('num_visits', 0) #按下直接歸0
        #request.session['num_visits'] = num_visits + 0

    context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    'num_visits': num_visits
    }

    return render(request, 'index.html', context=context)



    


#呼叫用django內建generic將book列表化輸出，此ListView會自動創建一個object_list或亦可用book_list
class BookListView(generic.ListView):
    model = Book
    #一頁允許最多十筆資料，若超過有翻頁功能(base模板的pagination)
    paginate_by = 10
    

    
#同上 會自動創建一個可以叫詳細資料的list 用法:object.author或book.author、.ISBN等
class BookDetailView(generic.DetailView):
    model = Book
    
    #book詳細資料
    def book_detail_view(request, primary_key):
        try:
            #取得model.py的Book資料
            book = Book.objects.get(pk=primary_key)
            
        except Book.DoesNotExist:
            raise Http404('Book does not exist')
        
        return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author
    

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key)
        except Author.DoesNotExist:
            raise Http404('Author does not exist')
        
    
        return render(request, 'catalog/author_detail.html', context={'author': author})

#查詢當前用戶已借書目
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    #找出當前用戶已借書目 
    def get_queryset(self): #似乎必須用get_queryset()
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back') 

#查詢所有已借出書目
class All_Borrowed(LoginRequiredMixin,PermissionRequiredMixin,generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name ='catalog/bookinstance_all_borrowed.html'
    paginate_by = 10
    def get_queryset(self): #似乎必須用get_queryset()
        return BookInstance.objects.filter(status__exact="o").order_by('due_back')





#檢查表單是否有效及請求類型
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):

    book_inst=get_object_or_404(BookInstance, pk = pk)
    #如果是POST
    if request.method == 'POST':
        form = RenewBookForm(request.POST)


        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed') )
    #如果不是POST，
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
            
'''
class BooksInstanceInline(InlineFormSetFactory):
    model = BookInstance
    fields = ['id', 'book','imprint','due_back','borrower','status',]
'''
class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    #initial={'date_of_death':'05/01/2018',}
    template_name_suffix = '_confirm_create'

class AuthorUpdate(UpdateView):
    model = Author
    #fields = ['first_name','last_name','date_of_birth','date_of_death']
    fields = '__all__'
    template_name_suffix = '_confirm_create'
    
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('author')

class BookCreate(CreateView):
    model = Book
    #fields = '__all__'
    fields = ['title', 'author', 'summary','isbn','genre']
    template_name_suffix = '_confirm_create'
    #inlines = [BooksInstanceInline] 


class BookUpdate(UpdateView):
    model = Book
    #fields = ['first_name','last_name','date_of_birth','date_of_death']
    fields = '__all__'
    template_name_suffix = '_confirm_create'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

