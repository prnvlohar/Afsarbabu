from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.shortcuts import get_object_or_404
from assessment.forms import (AssessmentForm, QuestionForm, RatingForm)
from assessment.models import ( Assessment, Question,
                               Rating, PassFailStatus)
from assessment.utils import send_email_with_marks

class ListAssessment(View):

    " Showing all assessment present in project "

    template_name = 'assessment/list_assessment.html'

    def get(self, request, *args, **kwargs):
        assessment = Assessment.objects.all()
        assessment = assessment.annotate(
            avg_rating=Avg('rating__rating', default=0))        
        return render(request, self.template_name, {'assessment': assessment,})

class AddAssessmentView(View):

    " Define assessment type and course "

    form_class = AssessmentForm
    template_name = 'assessment/addassessment.html'

    def get(self, request, *args, **kwargs):
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

class ShowAssessmentView(View):

    " Showing all assessment present in project "

    template_name = 'assessment/assessment.html'

    def get(self, request, *args, **kwargs):
        assessment = Assessment.objects.all()   
        return render(request, self.template_name, {'assessment': assessment,})


class AddAssessmentView(View):

    " Define assessment type and course "

    form_class = AssessmentForm
    template_name = 'assessment/addassessment.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = request.user

        if user.type == 'instructor':
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Assessment added successfully'})
            else:
                print(form.errors)
                return JsonResponse({'message': 'Assessment added failed'})
        else:
            return JsonResponse({'message': 'user is not instructor'})


class AddQuestionView(View):

    " Adding questions for assessment "

    form_class = QuestionForm
    template_name = "assessment/addQuestion.html"

    def get(self, request, *args, **kwargs):
        assessment_id = kwargs.get('pk')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        count = Question.objects.filter(assessment=assessment).count()
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'count':count,'assessment':assessment})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = request.user

        if user.type == 'instructor':
            if form.is_valid():
                assessment_id = kwargs.get('pk')
                assessment = get_object_or_404(Assessment, id=assessment_id)
                #insert assessment in form data
                form.instance.assessment = assessment
                form.save()
                messages.error(request, 'Question added successfully.')
                # return reverse of add-question with assessemnt id
                return HttpResponseRedirect(reverse('add-question', args=[assessment_id]))
            else:
                messages.error(request, 'Question add failed.')
                return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, 'User is not instructor.')
            return HttpResponseRedirect(reverse('index'))


class ShowQuizView(View):

    " Showing quiz according to user request "

    def get(self, request, *args, **kwargs):
        try:
            
            assessment = Assessment.objects.get(id=self.kwargs['pk'])
            
            questions = assessment.question_set.all()
            #retrive passfailmodel object
            passfail = PassFailStatus.objects.filter(user=request.user, assessment=assessment).first()
            return render(request, 'assessment/quiz.html', {'questions': questions,
                                                                'assessment': assessment,
                                                                'passfail':passfail,})

        except Exception as e:
            messages.success(
                request, e)
            return HttpResponseRedirect(reverse("show-assessment"))

    def post(self, request, *args, **kwargs):
        assessment = Assessment.objects.get(id=self.kwargs['pk'])
        if assessment.id in request.session:
            messages.success(request, 'Assessment already submitted.')
            return HttpResponseRedirect(reverse("show-assessment"))
        
        score = 0
        print("score")
        payload = request.POST
        questions = Question.objects.filter(assessment=assessment)
        for q in questions:
            if str(q.id) in payload:
                print("rtyuio")
                print(payload[str(q.id)], q.answer)
                if payload[str(q.id)] == q.answer:
                    print("inner")
                    score += 1
        
        print(score)
        # convert score into percentage
        score = score / len(questions) * 100
        print(score)
        #check score is above 80 and change status of passfail model
        if score > 80:
            try:
                passfail = PassFailStatus.objects.get(assessment=assessment, user=request.user)
            except:
                passfail = PassFailStatus(assessment=assessment, user=request.user)
            passfail.status = True
            passfail.save()
        else:
            try:
                passfail = PassFailStatus.objects.get(assessment=assessment, user=request.user)
            except:
                passfail = PassFailStatus(assessment=assessment, user=request.user)
            passfail.status = False
            passfail.save()
        
        request.session['assessment.id'] = True
        form = RatingForm
        # send_email_with_marks(request, score)x
        messages.success(
            request, 'Answer submmited successfully. Check your email for score.')
        return render(request, 'assessment/score.html', {'score': score, 'form': form,
                                                            'assessment': assessment})


def rating_quiz(request):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rating submmited successfully.')
            return HttpResponseRedirect(reverse("show-assessment"))
        else:
            messages.error(request, 'Assessment Rating Failed.')
            return HttpResponseRedirect(reverse("show-assessment"))


class QuestionListView(ListView):
    model = Question
    template_name = "assessment/question.html"

# class QuestionDetailView(DetailView):
#     model = Question
#     template_name = "assessment/question_detail.html"


class QuestionDeleteView(DeleteView):
    model = Question
    success_url = '/assessment/show-question/'
    template_name = "assessment/question_confirm_delete.html"


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['question']
    success_url = '/assessment/show-question/'
    template_name = "assessment/question_confirm_update.html"


