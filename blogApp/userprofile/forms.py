from django import forms
from django.contrib.auth.models import User
from .models import Profile

# 继承forms.Form，需要手动配置每个字段，适用于不与数据库进行直接交互的功能
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    
    
# 注册用户表单
class UserRegisterForm(forms.ModelForm):
    # 复写User的密码
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username','email')

    # 对两次密码是否一致进行检查
    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password')==data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("密码输入不一致，请重试。")


# Profile表单类
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone','avatar','bio')
