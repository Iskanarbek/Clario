from django.contrib import admin
from .models import DifficultyLevel, Term, RuleTheory, Problem, TestQuestion, UserProgress

@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'name')
    ordering = ('level',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty')
    list_filter = ('difficulty',)
    search_fields = ('title', 'explanation')

@admin.register(RuleTheory)
class RuleTheoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty')
    list_filter = ('difficulty',)
    search_fields = ('title', 'explanation')

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'difficulty')
    list_filter = ('difficulty',)
    search_fields = ('question', 'explanation')
    
    def question_short(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_short.short_description = 'Question'

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_short', 'difficulty')
    list_filter = ('difficulty',)
    search_fields = ('question', 'explanation')
    
    def question_short(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_short.short_description = 'Question'

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_level', 'placement_test_taken', 'placement_test_score')
    list_filter = ('current_level', 'placement_test_taken')
    search_fields = ('user__username',)