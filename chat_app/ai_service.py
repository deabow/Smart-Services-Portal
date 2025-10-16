import os
import json
import re
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from requests_app.models import Request, RequestStatus
from .models import ChatRoom, Message


class AIService:
    """خدمة الذكاء الاصطناعي المتقدمة للدردشة"""
    
    def __init__(self):
        self.context_memory = {}
        self.conversation_history = {}
        self.user_preferences = {}
        self.conversation_patterns = {}
        self.emotional_context = {}
        
    def process_message(self, chat_room: ChatRoom, content: str) -> Dict:
        """معالجة الرسالة باستخدام الذكاء الاصطناعي"""
        user_id = str(chat_room.user.id)
        
        # الحصول على تاريخ المحادثة
        conversation_history = self.get_conversation_history(chat_room)
        
        # تحليل الرسالة
        analysis = self.analyze_message(content, conversation_history)
        
        # إنشاء رد ذكي
        response = self.generate_intelligent_response(
            chat_room, content, analysis, conversation_history
        )
        
        # حفظ السياق
        self.update_context(user_id, content, analysis)
        
        return response
    
    def analyze_message(self, content: str, history: List[Dict]) -> Dict:
        """تحليل ذكي للرسالة"""
        content_lower = content.lower()
        
        # تحليل المشاعر
        sentiment = self.analyze_sentiment(content)
        
        # تحليل النية
        intent = self.analyze_intent(content, history)
        
        # استخراج الكيانات
        entities = self.extract_entities(content)
        
        # تحليل الأولوية
        priority = self.analyze_priority(content, entities)
        
        return {
            'sentiment': sentiment,
            'intent': intent,
            'entities': entities,
            'priority': priority,
            'length': len(content),
            'has_question': '?' in content or '؟' in content,
            'has_urgency': any(word in content_lower for word in ['عاجل', 'فوري', 'سريع', 'مستعجل']),
            'has_greeting': any(word in content_lower for word in ['مرحبا', 'السلام', 'أهلا', 'صباح', 'مساء']),
            'has_thanks': any(word in content_lower for word in ['شكرا', 'شكر', 'ممتاز', 'رائع']),
        }
    
    def analyze_sentiment(self, content: str) -> str:
        """تحليل مشاعر متقدم للرسالة"""
        # كلمات إيجابية متقدمة
        positive_words = {
            'شكرا': 3, 'ممتاز': 3, 'رائع': 3, 'جيد': 2, 'حلو': 2, 'مشكور': 3, 'أشكرك': 3,
            'ممتازة': 3, 'رائعة': 3, 'جميل': 2, 'حبيت': 2, 'عجبني': 2, 'مشكورة': 3,
            'أشكركم': 3, 'بارك الله فيكم': 4, 'جزاكم الله خيراً': 4, 'الله يبارك': 3
        }
        
        # كلمات سلبية متقدمة
        negative_words = {
            'مشكلة': 2, 'عطل': 2, 'تلف': 2, 'سيء': 3, 'مش راضي': 3, 'مش عاجبني': 3, 
            'غاضب': 4, 'زعلان': 3, 'مضايق': 3, 'مش راضي': 3, 'مش عاجبني': 3, 'مشكلة كبيرة': 4,
            'مشكلة خطيرة': 4, 'مشكلة مزعجة': 3, 'مشكلة صعبة': 3, 'مشكلة معقدة': 3
        }
        
        # كلمات عاجلة متقدمة
        urgent_words = {
            'عاجل': 4, 'فوري': 4, 'سريع': 3, 'مستعجل': 4, 'ضروري': 3, 'مشكلة عاجلة': 5,
            'مشكلة فورية': 5, 'مشكلة سريعة': 4, 'مشكلة مستعجلة': 5, 'مشكلة ضرورية': 4,
            'مشكلة خطيرة': 4, 'مشكلة كبيرة': 3, 'مشكلة مزعجة': 2
        }
        
        content_lower = content.lower()
        
        # حساب النقاط
        positive_score = sum(score for word, score in positive_words.items() if word in content_lower)
        negative_score = sum(score for word, score in negative_words.items() if word in content_lower)
        urgent_score = sum(score for word, score in urgent_words.items() if word in content_lower)
        
        # تحليل متقدم
        if urgent_score >= 4:
            return 'urgent'
        elif positive_score > negative_score and positive_score >= 3:
            return 'very_positive'
        elif positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score and negative_score >= 4:
            return 'very_negative'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_intent(self, content: str, history: List[Dict]) -> str:
        """تحليل نية المستخدم"""
        content_lower = content.lower()
        
        # نوايا الطلبات
        if any(word in content_lower for word in ['طلب', 'مشكلة', 'شكوى', 'عطل', 'تلف']):
            return 'create_request'
        
        # نوايا المتابعة
        if any(word in content_lower for word in ['حالة', 'متابعة', 'متى', 'أين', 'كيف']):
            return 'check_status'
        
        # نوايا البحث
        if any(word in content_lower for word in ['رقم', 'تتبع', 'بحث']):
            return 'search_request'
        
        # نوايا المساعدة
        if any(word in content_lower for word in ['مساعدة', 'معلومات', 'كيف', 'ماذا']):
            return 'help'
        
        # نوايا التحية
        if any(word in content_lower for word in ['مرحبا', 'السلام', 'أهلا']):
            return 'greeting'
        
        # نوايا الشكر
        if any(word in content_lower for word in ['شكرا', 'شكر', 'ممتاز']):
            return 'thanks'
        
        # نوايا الشكوى
        if any(word in content_lower for word in ['شكوى', 'مش راضي', 'مش عاجبني']):
            return 'complaint'
        
        return 'general'
    
    def extract_entities(self, content: str) -> Dict:
        """استخراج الكيانات من النص"""
        entities = {
            'tracking_numbers': re.findall(r'\b[A-Z0-9]{6,}\b', content.upper()),
            'phone_numbers': re.findall(r'\b01[0-9]{9}\b', content),
            'locations': self.extract_locations(content),
            'services': self.extract_services(content),
            'problems': self.extract_problems(content),
        }
        return entities
    
    def extract_locations(self, content: str) -> List[str]:
        """استخراج المواقع من النص"""
        locations = []
        content_lower = content.lower()
        
        location_keywords = [
            'منوف', 'السادات', 'سرس الليان', 'طملاي', 'شبشير', 'برهيم',
            'جزي', 'غمرين', 'بالمشط', 'كفر السنابسه', 'صنصفط', 'دمليج',
            'زاوية رزين', 'سدود', 'بهواش', 'كمشوش', 'فيشا', 'هيت',
            'سروهيت', 'دبركي', 'تتا', 'منشأة سلطان', 'سنجرج', 'شبرا بلوله',
            'الحامول', 'كفر العامره', 'كفر رماح', 'ميت ربيعه'
        ]
        
        for location in location_keywords:
            if location in content_lower:
                locations.append(location)
        
        return locations
    
    def extract_services(self, content: str) -> List[str]:
        """استخراج الخدمات من النص"""
        services = []
        content_lower = content.lower()
        
        service_keywords = {
            'مياه': ['مياه', 'ماء', 'شبكة المياه', 'خط المياه'],
            'كهرباء': ['كهرباء', 'تيار', 'شبكة الكهرباء', 'خط الكهرباء'],
            'طرق': ['طرق', 'شوارع', 'رصف', 'إسفلت', 'طريق'],
            'صرف': ['صرف', 'صرف صحي', 'مجاري', 'شبكة الصرف'],
            'إنارة': ['إنارة', 'أعمدة', 'أضواء', 'إضاءة'],
            'نظافة': ['نظافة', 'قمامة', 'نفايات', 'تنظيف'],
        }
        
        for service, keywords in service_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                services.append(service)
        
        return services
    
    def extract_problems(self, content: str) -> List[str]:
        """استخراج المشاكل من النص"""
        problems = []
        content_lower = content.lower()
        
        problem_keywords = {
            'عطل': ['عطل', 'توقف', 'لا يعمل', 'مش شغال'],
            'تلف': ['تلف', 'مكسور', 'مشوه', 'متهالك'],
            'انسداد': ['انسداد', 'مسدود', 'مش بيعدي'],
            'تسريب': ['تسريب', 'يقطر', 'مش بيقف'],
            'انقطاع': ['انقطاع', 'مقطوع', 'مش بيوصل'],
        }
        
        for problem, keywords in problem_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                problems.append(problem)
        
        return problems
    
    def analyze_priority(self, content: str, entities: Dict) -> int:
        """تحليل أولوية الرسالة (1-10)"""
        priority = 5  # افتراضي
        
        # زيادة الأولوية للكلمات العاجلة
        urgent_words = ['عاجل', 'فوري', 'سريع', 'مستعجل', 'ضروري', 'مشكلة كبيرة']
        if any(word in content.lower() for word in urgent_words):
            priority += 3
        
        # زيادة الأولوية للخدمات الأساسية
        if entities['services']:
            priority += 2
        
        # زيادة الأولوية للمشاكل
        if entities['problems']:
            priority += 2
        
        # زيادة الأولوية للرسائل الطويلة (مشاكل مفصلة)
        if len(content) > 100:
            priority += 1
        
        return min(priority, 10)
    
    def generate_intelligent_response(self, chat_room: ChatRoom, content: str, 
                                   analysis: Dict, history: List[Dict]) -> Dict:
        """إنشاء رد ذكي متقدم بناءً على التحليل"""
        intent = analysis['intent']
        sentiment = analysis['sentiment']
        entities = analysis['entities']
        
        # تحليل السياق المتقدم
        context_analysis = self.analyze_conversation_context(history, analysis)
        
        # إنشاء رد ذكي مع السياق
        if intent == 'create_request':
            return self.handle_create_request_advanced(chat_room, content, analysis, entities, context_analysis)
        elif intent == 'check_status':
            return self.handle_check_status_advanced(chat_room, analysis, entities, context_analysis)
        elif intent == 'search_request':
            return self.handle_search_request_advanced(chat_room, entities, context_analysis)
        elif intent == 'help':
            return self.handle_help_request_advanced(analysis, entities, context_analysis)
        elif intent == 'greeting':
            return self.handle_greeting_advanced(chat_room, analysis, context_analysis)
        elif intent == 'thanks':
            return self.handle_thanks_advanced(analysis, context_analysis)
        elif intent == 'complaint':
            return self.handle_complaint_advanced(chat_room, content, analysis, context_analysis)
        else:
            return self.handle_general_query_advanced(chat_room, content, analysis, entities, context_analysis)
    
    def analyze_conversation_context(self, history: List[Dict], analysis: Dict) -> Dict:
        """تحليل سياق المحادثة المتقدم"""
        context = {
            'conversation_length': len(history),
            'recent_topics': [],
            'user_mood_trend': 'stable',
            'conversation_phase': 'beginning',
            'repeated_concerns': [],
            'suggested_actions': []
        }
        
        # تحليل المواضيع الأخيرة
        if len(history) > 0:
            recent_messages = history[:5]  # آخر 5 رسائل
            topics = []
            for msg in recent_messages:
                if msg['message_type'] == 'user':
                    # استخراج المواضيع من الرسائل السابقة
                    if any(word in msg['content'].lower() for word in ['مياه', 'كهرباء', 'طرق']):
                        topics.append('infrastructure')
                    elif any(word in msg['content'].lower() for word in ['طلب', 'مشكلة']):
                        topics.append('requests')
                    elif any(word in msg['content'].lower() for word in ['شكر', 'ممتاز']):
                        topics.append('satisfaction')
            
            context['recent_topics'] = topics
        
        # تحديد مرحلة المحادثة
        if len(history) < 3:
            context['conversation_phase'] = 'beginning'
        elif len(history) < 10:
            context['conversation_phase'] = 'middle'
        else:
            context['conversation_phase'] = 'advanced'
        
        # تحليل الاتجاه العاطفي
        if analysis['sentiment'] in ['very_positive', 'positive']:
            context['user_mood_trend'] = 'positive'
        elif analysis['sentiment'] in ['very_negative', 'negative']:
            context['user_mood_trend'] = 'negative'
        elif analysis['sentiment'] == 'urgent':
            context['user_mood_trend'] = 'urgent'
        
        return context
    
    def handle_create_request_advanced(self, chat_room: ChatRoom, content: str, 
                                     analysis: Dict, entities: Dict, context: Dict) -> Dict:
        """معالجة متقدمة لطلب إنشاء طلب جديد"""
        # تحليل ذكي متقدم
        service_type = self.determine_service_type_advanced(entities['services'], context)
        problem_type = self.determine_problem_type_advanced(entities['problems'], analysis)
        urgency_level = self.calculate_urgency_level(analysis, entities, context)
        
        # إنشاء عنوان ذكي متقدم
        title = self.generate_smart_title_advanced(service_type, problem_type, entities['locations'], urgency_level)
        
        # إنشاء وصف محسن متقدم
        description = self.enhance_description_advanced(content, entities, analysis, context)
        
        # إنشاء اقتراح طلب ذكي
        from .models import ChatRequest
        chat_request = ChatRequest.objects.create(
            chat_room=chat_room,
            suggested_title=title,
            suggested_description=description,
            status='pending'
        )
        
        # إنشاء رد ذكي متقدم
        response_content = self.generate_request_response_advanced(
            service_type, problem_type, entities, analysis, title, urgency_level, context
        )
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=response_content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type,
            'chat_request_id': str(chat_request.id),
            'show_approval_buttons': True
        }
    
    def determine_service_type_advanced(self, services: List[str], context: Dict) -> str:
        """تحديد نوع الخدمة المتقدم"""
        if not services:
            # تحليل السياق لتحديد الخدمة المحتملة
            if 'infrastructure' in context['recent_topics']:
                return 'خدمة البنية التحتية'
            return 'خدمة عامة'
        
        service_priority = {
            'مياه': 1, 'كهرباء': 2, 'صرف': 3, 'طرق': 4, 'إنارة': 5, 'نظافة': 6
        }
        
        # اختيار الخدمة ذات الأولوية الأعلى مع مراعاة السياق
        return min(services, key=lambda x: service_priority.get(x, 99))
    
    def determine_problem_type_advanced(self, problems: List[str], analysis: Dict) -> str:
        """تحديد نوع المشكلة المتقدم"""
        if not problems:
            if analysis['sentiment'] == 'urgent':
                return 'مشكلة عاجلة'
            elif analysis['sentiment'] in ['very_negative', 'negative']:
                return 'مشكلة مزعجة'
            return 'مشكلة عامة'
        
        return problems[0]
    
    def calculate_urgency_level(self, analysis: Dict, entities: Dict, context: Dict) -> int:
        """حساب مستوى العجلة المتقدم"""
        urgency = analysis['priority']
        
        # زيادة العجلة حسب السياق
        if context['user_mood_trend'] == 'urgent':
            urgency += 2
        elif analysis['sentiment'] == 'urgent':
            urgency += 3
        
        # زيادة العجلة للخدمات الأساسية
        if entities['services']:
            urgency += 1
        
        return min(urgency, 10)
    
    def generate_smart_title_advanced(self, service_type: str, problem_type: str, 
                                    locations: List[str], urgency_level: int) -> str:
        """إنشاء عنوان ذكي متقدم"""
        location = locations[0] if locations else 'المنطقة'
        
        # إضافة مستوى العجلة للعنوان
        urgency_prefix = ""
        if urgency_level >= 8:
            urgency_prefix = "عاجل - "
        elif urgency_level >= 6:
            urgency_prefix = "مهم - "
        
        title_templates = {
            'مياه': f"{urgency_prefix}مشكلة في المياه - {location}",
            'كهرباء': f"{urgency_prefix}عطل في الكهرباء - {location}",
            'صرف': f"{urgency_prefix}مشكلة في الصرف الصحي - {location}",
            'طرق': f"{urgency_prefix}مشكلة في الطرق - {location}",
            'إنارة': f"{urgency_prefix}مشكلة في الإنارة - {location}",
            'نظافة': f"{urgency_prefix}مشكلة في النظافة - {location}",
        }
        
        return title_templates.get(service_type, f"{urgency_prefix}طلب خدمة - {location}")
    
    def enhance_description_advanced(self, content: str, entities: Dict, 
                                   analysis: Dict, context: Dict) -> str:
        """تحسين وصف الطلب المتقدم"""
        enhanced = content
        
        # إضافة تحليل المشاعر
        if analysis['sentiment'] == 'urgent':
            enhanced += "\n\n🚨 **مشكلة عاجلة تتطلب تدخل سريع**"
        elif analysis['sentiment'] in ['very_negative', 'negative']:
            enhanced += "\n\n⚠️ **مشكلة مزعجة تحتاج حل سريع**"
        
        # إضافة تفاصيل الموقع
        if entities['locations']:
            enhanced += f"\n\n📍 **الموقع:** {', '.join(entities['locations'])}"
        
        # إضافة تفاصيل الخدمة
        if entities['services']:
            enhanced += f"\n\n🔧 **نوع الخدمة:** {', '.join(entities['services'])}"
        
        # إضافة تفاصيل المشكلة
        if entities['problems']:
            enhanced += f"\n\n🔍 **نوع المشكلة:** {', '.join(entities['problems'])}"
        
        # إضافة السياق
        if context['conversation_phase'] == 'advanced':
            enhanced += f"\n\n💬 **تمت مناقشة هذه المشكلة في محادثة سابقة**"
        
        return enhanced
    
    def generate_request_response_advanced(self, service_type: str, problem_type: str, 
                                        entities: Dict, analysis: Dict, title: str, 
                                        urgency_level: int, context: Dict) -> str:
        """إنشاء رد ذكي متقدم لطلب إنشاء طلب"""
        # تحديد الأيقونة واللون حسب نوع الخدمة
        service_icons = {
            'مياه': '💧', 'كهرباء': '⚡', 'صرف': '🚰', 'طرق': '🛣️', 
            'إنارة': '💡', 'نظافة': '🧹'
        }
        
        icon = service_icons.get(service_type, '📋')
        
        # إنشاء رد مخصص حسب السياق
        if analysis['sentiment'] == 'urgent':
            urgency_text = "🚨 **أفهم أن هذه مشكلة عاجلة جداً!**"
            priority_text = f"🔥 **مستوى الأولوية: {urgency_level}/10**"
        elif analysis['sentiment'] in ['very_negative', 'negative']:
            urgency_text = "😔 **أفهم أنك تواجه مشكلة مزعجة**"
            priority_text = f"⚠️ **مستوى الأولوية: {urgency_level}/10**"
        else:
            urgency_text = "📝 **أفهم أنك تريد تقديم طلب**"
            priority_text = f"📊 **مستوى الأولوية: {urgency_level}/10**"
        
        # إضافة تحليل ذكي
        smart_analysis = self.generate_smart_analysis(entities, analysis, context)
        
        response = f"""{icon} {urgency_text}

{priority_text}

🔍 **تحليل ذكي لطلبك:**
{smart_analysis}

📝 **العنوان المقترح:** {title}

💡 **توقعاتي الذكية:**
• سأقوم بمعالجة طلبك بأولوية عالية
• ستحصل على رقم تتبع فوري للمتابعة
• سأتابع حالة طلبك باستمرار

هل تريد إنشاء طلب رسمي بهذه التفاصيل الذكية؟"""
        
        return response
    
    def generate_smart_analysis(self, entities: Dict, analysis: Dict, context: Dict) -> str:
        """إنشاء تحليل ذكي للطلب"""
        analysis_parts = []
        
        # تحليل الخدمة
        if entities['services']:
            service_analysis = {
                'مياه': "• المياه خدمة أساسية - سأعطيها أولوية قصوى",
                'كهرباء': "• الكهرباء خدمة حيوية - سأتابعها شخصياً",
                'صرف': "• الصرف الصحي مهم للصحة العامة - سأعطيها اهتمام خاص",
                'طرق': "• الطرق تؤثر على الحركة - سأتابعها بانتظام",
                'إنارة': "• الإنارة مهمة للأمان - سأتابعها بدقة",
                'نظافة': "• النظافة مهمة للمظهر العام - سأتابعها باهتمام"
            }
            
            for service in entities['services']:
                if service in service_analysis:
                    analysis_parts.append(service_analysis[service])
        
        # تحليل المشكلة
        if entities['problems']:
            problem_analysis = {
                'عطل': "• العطل يتطلب إصلاح فوري - سأتابع مع الفنيين",
                'تلف': "• التلف يحتاج استبدال - سأتابع مع الموردين",
                'انسداد': "• الانسداد يحتاج تنظيف - سأتابع مع عمال النظافة",
                'تسريب': "• التسريب خطر - سأتابع مع السباكين",
                'انقطاع': "• الانقطاع مزعج - سأتابع مع الشركة"
            }
            
            for problem in entities['problems']:
                if problem in problem_analysis:
                    analysis_parts.append(problem_analysis[problem])
        
        # تحليل السياق
        if context['user_mood_trend'] == 'urgent':
            analysis_parts.append("• أفهم أنك في حالة عجلة - سأعطي طلبك أولوية قصوى")
        elif context['user_mood_trend'] == 'negative':
            analysis_parts.append("• أفهم إحباطك - سأعمل على حل مشكلتك بسرعة")
        
        if not analysis_parts:
            analysis_parts.append("• سأتابع طلبك بدقة وأعطيك تحديثات مستمرة")
        
        return "\n".join(analysis_parts)
    
    def handle_create_request(self, chat_room: ChatRoom, content: str, 
                            analysis: Dict, entities: Dict) -> Dict:
        """معالجة طلب إنشاء طلب جديد"""
        # تحديد نوع الطلب حسب الخدمات المكتشفة
        service_type = self.determine_service_type(entities['services'])
        problem_type = self.determine_problem_type(entities['problems'])
        
        # إنشاء عنوان ذكي
        title = self.generate_smart_title(service_type, problem_type, entities['locations'])
        
        # إنشاء وصف محسن
        description = self.enhance_description(content, entities)
        
        # إنشاء اقتراح طلب
        from .models import ChatRequest
        chat_request = ChatRequest.objects.create(
            chat_room=chat_room,
            suggested_title=title,
            suggested_description=description,
            status='pending'
        )
        
        # إنشاء رد ذكي
        response_content = self.generate_request_response(
            service_type, problem_type, entities, analysis, title
        )
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=response_content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type,
            'chat_request_id': str(chat_request.id),
            'show_approval_buttons': True
        }
    
    def determine_service_type(self, services: List[str]) -> str:
        """تحديد نوع الخدمة"""
        if not services:
            return 'خدمة عامة'
        
        service_priority = {
            'مياه': 1,
            'كهرباء': 2,
            'صرف': 3,
            'طرق': 4,
            'إنارة': 5,
            'نظافة': 6
        }
        
        # اختيار الخدمة ذات الأولوية الأعلى
        return min(services, key=lambda x: service_priority.get(x, 99))
    
    def determine_problem_type(self, problems: List[str]) -> str:
        """تحديد نوع المشكلة"""
        if not problems:
            return 'مشكلة عامة'
        
        return problems[0]  # أول مشكلة مكتشفة
    
    def generate_smart_title(self, service_type: str, problem_type: str, locations: List[str]) -> str:
        """إنشاء عنوان ذكي للطلب"""
        location = locations[0] if locations else 'المنطقة'
        
        title_templates = {
            'مياه': f"مشكلة في المياه - {location}",
            'كهرباء': f"عطل في الكهرباء - {location}",
            'صرف': f"مشكلة في الصرف الصحي - {location}",
            'طرق': f"مشكلة في الطرق - {location}",
            'إنارة': f"مشكلة في الإنارة - {location}",
            'نظافة': f"مشكلة في النظافة - {location}",
        }
        
        return title_templates.get(service_type, f"طلب خدمة - {location}")
    
    def enhance_description(self, content: str, entities: Dict) -> str:
        """تحسين وصف الطلب"""
        enhanced = content
        
        # إضافة تفاصيل الموقع
        if entities['locations']:
            enhanced += f"\n\nالموقع: {', '.join(entities['locations'])}"
        
        # إضافة تفاصيل الخدمة
        if entities['services']:
            enhanced += f"\n\nنوع الخدمة: {', '.join(entities['services'])}"
        
        # إضافة تفاصيل المشكلة
        if entities['problems']:
            enhanced += f"\n\nنوع المشكلة: {', '.join(entities['problems'])}"
        
        return enhanced
    
    def generate_request_response(self, service_type: str, problem_type: str, 
                               entities: Dict, analysis: Dict, title: str) -> str:
        """إنشاء رد ذكي لطلب إنشاء طلب"""
        # تحديد الأيقونة واللون حسب نوع الخدمة
        service_icons = {
            'مياه': '💧',
            'كهرباء': '⚡',
            'صرف': '🚰',
            'طرق': '🛣️',
            'إنارة': '💡',
            'نظافة': '🧹',
        }
        
        icon = service_icons.get(service_type, '📋')
        
        # إنشاء رد مخصص
        if analysis['sentiment'] == 'urgent':
            urgency_text = "🚨 أفهم أن هذه مشكلة عاجلة"
        elif analysis['sentiment'] == 'negative':
            urgency_text = "⚠️ أفهم أنك تواجه مشكلة مزعجة"
        else:
            urgency_text = "📝 أفهم أنك تريد تقديم طلب"
        
        response = f"""{icon} {urgency_text}

🔍 **تحليل طلبك:**
• نوع الخدمة: {service_type}
• نوع المشكلة: {problem_type}
• الأولوية: {analysis['priority']}/10

📝 **العنوان المقترح:** {title}

هل تريد إنشاء طلب رسمي بهذه التفاصيل؟"""
        
        return response
    
    def handle_check_status(self, chat_room: ChatRoom, analysis: Dict, entities: Dict) -> Dict:
        """معالجة طلب فحص حالة الطلبات"""
        # الحصول على طلبات المستخدم
        requests = Request.objects.filter(user=chat_room.user).order_by('-created_at')[:5]
        
        if not requests:
            content = """📋 **لا توجد طلبات مسجلة لك حالياً**

💡 **يمكنك:**
• تقديم طلب جديد بكتابة "طلب" + وصف المشكلة
• الحصول على مساعدة بكتابة "مساعدة"
• معرفة الخدمات المتاحة بكتابة "خدمات" """
        else:
            content = self.generate_status_report(requests, analysis)
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type
        }
    
    def generate_status_report(self, requests: List[Request], analysis: Dict) -> str:
        """إنشاء تقرير حالة الطلبات"""
        content = "📊 **تقرير حالة طلباتك:**\n\n"
        
        status_icons = {
            'قيد المراجعة': '⏳',
            'مكتمل': '✅',
            'قيد التنفيذ': '🔄',
            'مرفوض': '❌',
            'معلق': '⏸️'
        }
        
        for i, req in enumerate(requests, 1):
            icon = status_icons.get(req.status.name, '📋')
            
            content += f"{i}. {icon} **{req.title}**\n"
            content += f"   📋 الحالة: {req.status.name}\n"
            content += f"   🔢 رقم التتبع: `{req.tracking_number}`\n"
            content += f"   📅 التاريخ: {req.created_at.strftime('%Y-%m-%d')}\n"
            
            # إضافة توقعات زمنية
            if req.status.name == 'قيد المراجعة':
                content += f"   ⏰ متوقع الانتهاء: خلال 3-5 أيام عمل\n"
            elif req.status.name == 'قيد التنفيذ':
                content += f"   ⏰ متوقع الانتهاء: خلال 1-2 يوم\n"
            
            content += "\n"
        
        # إضافة نصائح ذكية
        content += "💡 **نصائح ذكية:**\n"
        content += "• اكتب رقم التتبع للبحث عن طلب محدد\n"
        content += "• للاستفسار عن طلب معين، اكتب رقم التتبع\n"
        content += "• لتقديم طلب جديد، اكتب 'طلب' + وصف المشكلة\n"
        
        return content
    
    def handle_search_request(self, chat_room: ChatRoom, entities: Dict) -> Dict:
        """معالجة البحث عن طلب محدد"""
        tracking_numbers = entities['tracking_numbers']
        
        if not tracking_numbers:
            content = """🔍 **للبحث عن طلب محدد:**

يرجى كتابة رقم التتبع الخاص بالطلب.

💡 **مثال:** ABC12345

أو اكتب 'حالة طلباتي' لرؤية جميع طلباتك."""
        else:
            # البحث عن الطلب
            tracking_number = tracking_numbers[0]
            try:
                request = Request.objects.get(
                    tracking_number=tracking_number,
                    user=chat_room.user
                )
                content = self.generate_detailed_request_info(request)
            except Request.DoesNotExist:
                content = f"""❌ **لم أجد طلباً برقم التتبع:** `{tracking_number}`

🔍 **تحقق من:**
• أن رقم التتبع صحيح
• أن الطلب مسجل باسمك
• أن الطلب لم يتم حذفه

💡 **يمكنك:**
• كتابة 'حالة طلباتي' لرؤية جميع طلباتك
• كتابة 'طلب جديد' لتقديم طلب جديد"""
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type
        }
    
    def generate_detailed_request_info(self, request: Request) -> str:
        """إنشاء معلومات مفصلة عن الطلب"""
        status_icons = {
            'قيد المراجعة': '⏳',
            'مكتمل': '✅',
            'قيد التنفيذ': '🔄',
            'مرفوض': '❌',
            'معلق': '⏸️'
        }
        
        icon = status_icons.get(request.status.name, '📋')
        
        content = f"""🔍 **تفاصيل طلبك:**

{icon} **{request.title}**
📋 **الحالة:** {request.status.name}
🔢 **رقم التتبع:** `{request.tracking_number}`
📅 **تاريخ الإنشاء:** {request.created_at.strftime('%Y-%m-%d %H:%M')}
📝 **الوصف:** {request.description}

**آخر تحديث:** {request.updated_at.strftime('%Y-%m-%d %H:%M')}"""
        
        # إضافة معلومات إضافية حسب الحالة
        if request.status.name == 'قيد المراجعة':
            content += "\n\n⏰ **متوقع الانتهاء:** خلال 3-5 أيام عمل"
        elif request.status.name == 'قيد التنفيذ':
            content += "\n\n⏰ **متوقع الانتهاء:** خلال 1-2 يوم"
        elif request.status.name == 'مكتمل':
            content += "\n\n🎉 **تم إنجاز طلبك بنجاح!**"
        elif request.status.name == 'مرفوض':
            content += "\n\n❌ **تم رفض الطلب.** يمكنك تقديم طلب جديد."
        
        return content
    
    def handle_help_request(self, analysis: Dict, entities: Dict) -> Dict:
        """معالجة طلب المساعدة"""
        # إنشاء رد مساعدة مخصص حسب السياق
        if entities['services']:
            service_help = self.generate_service_specific_help(entities['services'])
        else:
            service_help = self.generate_general_help()
        
        return {
            'content': service_help,
            'message_type': 'bot'
        }
    
    def generate_service_specific_help(self, services: List[str]) -> str:
        """إنشاء مساعدة مخصصة للخدمات"""
        service_help = {
            'مياه': """💧 **مساعدة مشاكل المياه:**

🔧 **المشاكل الشائعة:**
• انقطاع المياه
• ضعف الضغط
• تسريب في الشبكة
• مياه غير صالحة للشرب

📞 **خطوات الحل:**
1. تحقق من الصنبور الرئيسي
2. اتصل بشركة المياه
3. قدم طلب إصلاح رسمي

💡 **نصائح:**
• احتفظ برقم الطلب للمتابعة
• التقط صور للمشكلة إن أمكن""",
            
            'كهرباء': """⚡ **مساعدة مشاكل الكهرباء:**

🔧 **المشاكل الشائعة:**
• انقطاع التيار
• ضعف الجهد
• عطل في العدادات
• مشاكل في الأسلاك

📞 **خطوات الحل:**
1. تحقق من القواطع
2. اتصل بشركة الكهرباء
3. قدم طلب إصلاح رسمي

⚠️ **تحذير:** لا تلمس الأسلاك المكشوفة""",
            
            'طرق': """🛣️ **مساعدة مشاكل الطرق:**

🔧 **المشاكل الشائعة:**
• حفر في الطريق
• تلف الإسفلت
• مشاكل في الرصف
• انسداد المجاري

📞 **خطوات الحل:**
1. حدد موقع المشكلة بدقة
2. قدم طلب إصلاح رسمي
3. تابع حالة الطلب

💡 **نصائح:**
• اذكر الشارع والمنطقة
• التقط صور للمشكلة"""
        }
        
        # دمج مساعدة الخدمات المطلوبة
        help_text = "🤖 **مساعدة مخصصة لك:**\n\n"
        for service in services:
            if service in service_help:
                help_text += service_help[service] + "\n\n"
        
        return help_text
    
    def generate_general_help(self) -> str:
        """إنشاء مساعدة عامة"""
        return """🤖 **كيف يمكنني مساعدتك؟**

يمكنني مساعدتك في:

📝 **تقديم الطلبات:**
• اكتب "طلب" + وصف المشكلة
• سأساعدك في إنشاء طلب رسمي
• سأحلل مشكلتك وأقترح الحلول

📊 **متابعة الطلبات:**
• اكتب "حالة طلباتي" لرؤية جميع الطلبات
• اكتب رقم التتبع للبحث عن طلب محدد
• سأعطيك توقعات زمنية للانتهاء

🔍 **البحث والاستعلام:**
• اكتب رقم التتبع للبحث عن طلب
• اكتب "معلومات" للحصول على معلومات عامة
• اكتب "خدمات" لمعرفة الخدمات المتاحة

💡 **نصائح للاستخدام الأمثل:**
• كن واضحاً في وصف مشكلتك
• اذكر المكان والتفاصيل المهمة
• يمكنك متابعة طلباتك في أي وقت
• أنا أتعلم من كل محادثة لأخدمك بشكل أفضل

🎯 **أمثلة على الاستخدام:**
• "مشكلة في المياه في شارع النيل"
• "حالة طلباتي"
• "ABC12345"
• "مساعدة مشاكل الكهرباء" """
    
    def handle_greeting_advanced(self, chat_room: ChatRoom, analysis: Dict, context: Dict) -> Dict:
        """معالجة متقدمة للتحية"""
        user_name = chat_room.user.full_name or chat_room.user.username
        
        # تحليل ذكي للمستخدم
        user_analysis = self.analyze_user_patterns(chat_room.user)
        
        # الحصول على آخر طلب للمستخدم
        last_request = Request.objects.filter(user=chat_room.user).order_by('-created_at').first()
        
        # إنشاء تحية مخصصة حسب السياق
        if context['conversation_phase'] == 'beginning':
            greeting_style = "أهلاً وسهلاً بك"
        elif context['conversation_phase'] == 'middle':
            greeting_style = "مرحباً بك مرة أخرى"
        else:
            greeting_style = "أهلاً وسهلاً بك مرة أخرى"
        
        if last_request:
            # تحليل حالة آخر طلب
            status_analysis = self.analyze_request_status(last_request)
            
            content = f"""👋 **{greeting_style} {user_name}!**

{status_analysis}

🤖 **أنا مساعدك الذكي المتقدم** ويمكنني:
• تحليل مشاكلك بذكاء اصطناعي
• اقتراح حلول مخصصة لك
• متابعة طلباتك بدقة فائقة
• توقع احتياجاتك المستقبلية

💡 **اقتراحاتي الذكية لك:**
{self.generate_smart_suggestions(user_analysis, last_request)}

كيف يمكنني مساعدتك اليوم؟"""
        else:
            content = f"""👋 **{greeting_style} {user_name}!**

أهلاً وسهلاً بك في خدمة المواطنين الذكية المتقدمة!

🧠 **أنا مساعدك الذكي الفائق** ويمكنني:
• تحليل مشاكلك بذكاء اصطناعي متقدم
• اقتراح حلول مخصصة ومبتكرة
• توقع احتياجاتك قبل أن تطلبها
• متابعة طلباتك بدقة فائقة
• تعلم من كل محادثة لأخدمك بشكل أفضل

🎯 **مميزاتي الذكية:**
• فهم المشاعر والسياق
• تحليل أنماط الاستخدام
• اقتراحات استباقية
• ردود مخصصة 100%

كيف يمكنني مساعدتك اليوم؟"""
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type
        }
    
    def analyze_user_patterns(self, user) -> Dict:
        """تحليل أنماط المستخدم"""
        # تحليل طلبات المستخدم
        total_requests = Request.objects.filter(user=user).count()
        completed_requests = Request.objects.filter(user=user, status__name="مكتمل").count()
        
        # تحليل أنواع الخدمات المفضلة
        recent_requests = Request.objects.filter(user=user).order_by('-created_at')[:5]
        service_preferences = []
        
        for req in recent_requests:
            if 'مياه' in req.title.lower():
                service_preferences.append('مياه')
            elif 'كهرباء' in req.title.lower():
                service_preferences.append('كهرباء')
            elif 'طرق' in req.title.lower():
                service_preferences.append('طرق')
        
        return {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'service_preferences': service_preferences,
            'is_active_user': total_requests > 0,
            'success_rate': (completed_requests / total_requests * 100) if total_requests > 0 else 0
        }
    
    def analyze_request_status(self, request: Request) -> str:
        """تحليل حالة الطلب"""
        status_icons = {
            'قيد المراجعة': '⏳',
            'مكتمل': '✅',
            'قيد التنفيذ': '🔄',
            'مرفوض': '❌',
            'معلق': '⏸️'
        }
        
        icon = status_icons.get(request.status.name, '📋')
        
        if request.status.name == 'قيد المراجعة':
            return f"""📋 **آخر طلب لك:** {request.title}
{icon} **الحالة:** {request.status.name}
⏰ **متوقع الانتهاء:** خلال 3-5 أيام عمل
💡 **نصيحتي:** يمكنك متابعة طلبك بكتابة رقم التتبع"""
        elif request.status.name == 'قيد التنفيذ':
            return f"""📋 **آخر طلب لك:** {request.title}
{icon} **الحالة:** {request.status.name}
⏰ **متوقع الانتهاء:** خلال 1-2 يوم
🎉 **أخبار جيدة:** طلبك قيد التنفيذ الآن!"""
        elif request.status.name == 'مكتمل':
            return f"""📋 **آخر طلب لك:** {request.title}
{icon} **الحالة:** {request.status.name}
🎉 **ممتاز:** تم إنجاز طلبك بنجاح!
💡 **نصيحتي:** هل تريد تقديم طلب جديد؟"""
        else:
            return f"""📋 **آخر طلب لك:** {request.title}
{icon} **الحالة:** {request.status.name}
💡 **نصيحتي:** يمكنك تقديم طلب جديد أو متابعة الطلبات الأخرى"""
    
    def generate_smart_suggestions(self, user_analysis: Dict, last_request: Request) -> str:
        """إنشاء اقتراحات ذكية للمستخدم"""
        suggestions = []
        
        if user_analysis['is_active_user']:
            if user_analysis['success_rate'] > 80:
                suggestions.append("• أنت مستخدم ممتاز! يمكنني مساعدتك في طلبات أكثر تعقيداً")
            elif user_analysis['success_rate'] > 50:
                suggestions.append("• أنت مستخدم جيد! يمكنني تحسين طلباتك أكثر")
            else:
                suggestions.append("• يمكنني مساعدتك في تحسين جودة طلباتك")
        
        if user_analysis['service_preferences']:
            most_common = max(set(user_analysis['service_preferences']), key=user_analysis['service_preferences'].count)
            suggestions.append(f"• أرى أنك مهتم بـ{most_common} - يمكنني مساعدتك في مشاكل مشابهة")
        
        if last_request and last_request.status.name == 'مكتمل':
            suggestions.append("• طلبك الأخير تم بنجاح! هل تريد تقديم طلب جديد؟")
        elif last_request and last_request.status.name == 'قيد المراجعة':
            suggestions.append("• طلبك قيد المراجعة - يمكنني متابعته لك")
        
        if not suggestions:
            suggestions.append("• يمكنني مساعدتك في تقديم طلب جديد")
            suggestions.append("• يمكنني الإجابة على استفساراتك")
        
        return "\n".join(suggestions)
    
    def handle_greeting(self, chat_room: ChatRoom, analysis: Dict) -> Dict:
        """معالجة التحية (النسخة القديمة للتوافق)"""
        return self.handle_greeting_advanced(chat_room, analysis, {'conversation_phase': 'beginning'})
    
    def handle_thanks_advanced(self, analysis: Dict, context: Dict) -> Dict:
        """معالجة متقدمة للشكر"""
        # تحليل مستوى الشكر
        if analysis['sentiment'] == 'very_positive':
            responses = [
                "🎉 **شكراً لك كثيراً!** أنا سعيد جداً لأنني استطعت مساعدتك!",
                "😊 **العفو!** هذا شرف لي أن أخدمك! هل تريد مساعدة في شيء آخر؟",
                "🌟 **شكراً لك!** أنا فخور بأنني استطعت مساعدتك! هل تريد مساعدة أخرى؟",
                "💖 **العفو!** أنا هنا دائماً لخدمتك! هل تريد تقديم طلب جديد؟",
                "🎯 **شكراً لك!** أنا متحمس لمساعدتك أكثر! هل تريد مساعدة في شيء آخر؟"
            ]
        else:
            responses = [
                "شكراً لك! أنا هنا دائماً لمساعدتك. هل تريد مساعدة في شيء آخر؟",
                "العفو! هذا واجبي. هل يمكنني مساعدتك في شيء آخر؟",
                "شكراً لك! سعيد لأنني استطعت مساعدتك. هل تريد مساعدة أخرى؟",
                "العفو! أنا هنا لخدمتك. هل تريد تقديم طلب جديد أو متابعة طلب موجود؟",
                "شكراً لك! هل تريد مساعدة في شيء آخر؟"
            ]
        
        # إضافة اقتراحات ذكية حسب السياق
        if context['conversation_phase'] == 'advanced':
            smart_suggestions = self.generate_contextual_suggestions(context)
            responses = [f"{response}\n\n💡 **اقتراحاتي الذكية:**\n{smart_suggestions}" for response in responses]
        
        content = random.choice(responses)
        
        return {
            'content': content,
            'message_type': 'bot'
        }
    
    def generate_contextual_suggestions(self, context: Dict) -> str:
        """إنشاء اقتراحات مخصصة حسب السياق"""
        suggestions = []
        
        if 'infrastructure' in context['recent_topics']:
            suggestions.append("• يمكنني مساعدتك في مشاكل البنية التحتية الأخرى")
        
        if context['user_mood_trend'] == 'positive':
            suggestions.append("• أنت في مزاج جيد! هل تريد تقديم طلب جديد؟")
        
        if context['conversation_phase'] == 'advanced':
            suggestions.append("• يمكنني تحليل مشاكلك بشكل أعمق")
            suggestions.append("• يمكنني اقتراح حلول مبتكرة")
        
        if not suggestions:
            suggestions.append("• يمكنني مساعدتك في تقديم طلب جديد")
            suggestions.append("• يمكنني الإجابة على استفساراتك")
        
        return "\n".join(suggestions)
    
    def handle_thanks(self, analysis: Dict) -> Dict:
        """معالجة الشكر (النسخة القديمة للتوافق)"""
        return self.handle_thanks_advanced(analysis, {'conversation_phase': 'beginning'})
    
    def handle_complaint_advanced(self, chat_room: ChatRoom, content: str, analysis: Dict, context: Dict) -> Dict:
        """معالجة متقدمة للشكاوى"""
        # تحليل مستوى الشكوى
        complaint_level = self.analyze_complaint_level(content, analysis)
        
        # إنشاء رد متعاطف متقدم
        if complaint_level == 'high':
            empathy_response = "😔 **أفهم إحباطك العميق وأعتذر بشدة عن المشكلة**"
            urgency_text = "🚨 **سأعطي شكواك أولوية قصوى**"
        elif complaint_level == 'medium':
            empathy_response = "😔 **أفهم إحباطك وأعتذر عن المشكلة**"
            urgency_text = "⚠️ **سأعطي شكواك أولوية عالية**"
        else:
            empathy_response = "😔 **أفهم قلقك وأعتذر عن المشكلة**"
            urgency_text = "📝 **سأتابع شكواك بدقة**"
        
        # تحليل المشكلة وتقديم حلول
        problem_analysis = self.analyze_complaint_problem(content, analysis)
        suggested_solutions = self.generate_complaint_solutions(analysis, context)
        
        content = f"""{empathy_response}

{urgency_text}

🔍 **تحليل شكواك:**
{problem_analysis}

💡 **الحلول المقترحة:**
{suggested_solutions}

📝 **هل تريد:**
• تقديم شكوى رسمية فورية؟
• متابعة شكوى سابقة؟
• الحصول على مساعدة متخصصة؟

🎯 **يمكنني:**
• تحليل مشكلتك بالتفصيل
• توجيهك للجهة المناسبة
• متابعة شكواك حتى الحل
• تقديم حلول بديلة

كيف يمكنني مساعدتك في حل هذه المشكلة؟"""
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type
        }
    
    def analyze_complaint_level(self, content: str, analysis: Dict) -> str:
        """تحليل مستوى الشكوى"""
        content_lower = content.lower()
        
        # كلمات تدل على شكوى عالية
        high_complaint_words = ['غاضب', 'زعلان', 'مضايق', 'مش راضي', 'مش عاجبني', 'مشكلة كبيرة', 'مشكلة خطيرة']
        
        # كلمات تدل على شكوى متوسطة
        medium_complaint_words = ['مشكلة', 'عطل', 'تلف', 'مشكلة مزعجة', 'مشكلة صعبة']
        
        if any(word in content_lower for word in high_complaint_words):
            return 'high'
        elif any(word in content_lower for word in medium_complaint_words):
            return 'medium'
        else:
            return 'low'
    
    def analyze_complaint_problem(self, content: str, analysis: Dict) -> str:
        """تحليل مشكلة الشكوى"""
        analysis_parts = []
        
        if analysis['sentiment'] == 'urgent':
            analysis_parts.append("• أفهم أن هذه مشكلة عاجلة تتطلب حل فوري")
        elif analysis['sentiment'] in ['very_negative', 'negative']:
            analysis_parts.append("• أفهم أنك تواجه مشكلة مزعجة")
        
        if analysis['has_urgency']:
            analysis_parts.append("• أفهم أنك في حالة عجلة")
        
        if len(content) > 100:
            analysis_parts.append("• أفهم أن المشكلة معقدة وتحتاج تحليل دقيق")
        
        if not analysis_parts:
            analysis_parts.append("• سأحلل مشكلتك بدقة وأقدم لك الحلول المناسبة")
        
        return "\n".join(analysis_parts)
    
    def generate_complaint_solutions(self, analysis: Dict, context: Dict) -> str:
        """إنشاء حلول للشكوى"""
        solutions = []
        
        if analysis['sentiment'] == 'urgent':
            solutions.append("• سأقوم بإنشاء طلب عاجل فوراً")
            solutions.append("• سأتابع مع الجهة المسؤولة شخصياً")
        else:
            solutions.append("• سأقوم بإنشاء طلب رسمي")
            solutions.append("• سأتابع حالة طلبك بدقة")
        
        if context['user_mood_trend'] == 'negative':
            solutions.append("• سأقدم لك حلول بديلة")
            solutions.append("• سأتابع معك شخصياً حتى الحل")
        
        solutions.append("• سأعطيك رقم تتبع للمتابعة")
        solutions.append("• سأتابع حالة طلبك باستمرار")
        
        return "\n".join(solutions)
    
    def handle_complaint(self, chat_room: ChatRoom, content: str, analysis: Dict) -> Dict:
        """معالجة الشكاوى (النسخة القديمة للتوافق)"""
        return self.handle_complaint_advanced(chat_room, content, analysis, {'conversation_phase': 'beginning'})
    
    def handle_general_query_advanced(self, chat_room: ChatRoom, content: str, 
                                    analysis: Dict, entities: Dict, context: Dict) -> Dict:
        """معالجة متقدمة للاستفسارات العامة"""
        # تحليل ذكي متقدم للاستفسار
        query_analysis = self.analyze_general_query(content, analysis, entities, context)
        
        # إنشاء رد ذكي متقدم
        if analysis['has_question']:
            response_content = self.generate_question_response_advanced(content, analysis, entities, context)
        elif analysis['sentiment'] == 'urgent':
            response_content = self.generate_urgent_response_advanced(content, analysis, entities, context)
        elif len(content) > 100:
            response_content = self.generate_detailed_response_advanced(content, analysis, entities, context)
        else:
            response_content = self.generate_general_response_advanced(content, analysis, entities, context)
        
        bot_message = Message.objects.create(
            chat_room=chat_room,
            message_type='bot',
            content=response_content
        )
        
        return {
            'id': str(bot_message.id),
            'content': bot_message.content,
            'created_at': bot_message.created_at.isoformat(),
            'message_type': bot_message.message_type
        }
    
    def analyze_general_query(self, content: str, analysis: Dict, entities: Dict, context: Dict) -> Dict:
        """تحليل ذكي للاستفسار العام"""
        return {
            'complexity': 'high' if len(content) > 100 else 'medium' if len(content) > 50 else 'low',
            'has_entities': bool(entities['services'] or entities['problems'] or entities['locations']),
            'context_relevant': context['conversation_phase'] == 'advanced',
            'user_mood': context['user_mood_trend'],
            'needs_clarification': analysis['has_question'] and not entities['services']
        }
    
    def generate_question_response_advanced(self, content: str, analysis: Dict, entities: Dict, context: Dict) -> str:
        """إنشاء رد متقدم للأسئلة"""
        if entities['services']:
            service_help = self.generate_service_specific_help(entities['services'])
            return f"""🤔 **سؤال ممتاز ومحدد!**

{service_help}

💡 **بناءً على سؤالك، أقترح:**
• كتابة "طلب" لتقديم طلب رسمي
• كتابة "مساعدة" للحصول على مساعدة إضافية
• كتابة "معلومات" للحصول على تفاصيل أكثر

كيف يمكنني مساعدتك بشكل أفضل؟"""
        else:
            return f"""🤔 **سؤال ممتاز!**

أفهم سؤالك وأقدر اهتمامك. دعني أساعدك في الحصول على إجابة شاملة.

🧠 **تحليلي الذكي لسؤالك:**
• أفهم أنك تبحث عن معلومات محددة
• سأقدم لك إجابة شاملة ومفصلة
• سأقترح عليك خطوات عملية

💡 **اقتراحاتي الذكية:**
• كتابة "مساعدة" للحصول على معلومات عامة
• كتابة "خدمات" لمعرفة الخدمات المتاحة
• كتابة "معلومات" للحصول على تفاصيل أكثر

🔍 **أو يمكنك:**
• وصف مشكلتك بالتفصيل وسأساعدك في حلها
• كتابة "طلب" إذا كنت تريد تقديم طلب رسمي

كيف يمكنني مساعدتك بشكل أفضل؟"""
    
    def generate_urgent_response_advanced(self, content: str, analysis: Dict, entities: Dict, context: Dict) -> str:
        """إنشاء رد متقدم للرسائل العاجلة"""
        urgency_level = analysis['priority']
        
        if urgency_level >= 8:
            urgency_text = "🚨 **أفهم أن هذه مشكلة عاجلة جداً!**"
            priority_text = f"🔥 **مستوى الأولوية: {urgency_level}/10**"
            action_text = "سأقوم بمعالجة طلبك بأولوية قصوى فوراً!"
        else:
            urgency_text = "⚠️ **أفهم أن هذه مشكلة عاجلة!**"
            priority_text = f"⚡ **مستوى الأولوية: {urgency_level}/10**"
            action_text = "سأقوم بمعالجة طلبك بأولوية عالية!"
        
        return f"""{urgency_text}

{priority_text}

{action_text}

🎯 **خطواتي الذكية:**
• سأقوم بإنشاء طلب رسمي فوراً
• سأعطيك رقم تتبع للمتابعة
• سأتابع حالة طلبك باستمرار
• سأعطيك تحديثات فورية

💡 **هل تريد:**
• إنشاء طلب رسمي الآن؟
• الحصول على رقم تتبع للمتابعة؟
• معرفة الخطوات التالية؟

اكتب "نعم" لإنشاء الطلب فوراً!"""
    
    def generate_detailed_response_advanced(self, content: str, analysis: Dict, entities: Dict, context: Dict) -> str:
        """إنشاء رد متقدم للرسائل المفصلة"""
        return f"""📝 **شكراً لك على الشرح المفصل والواضح!**

أقدر أنك أخذت وقتك لوصف مشكلتك بالتفصيل. هذا يساعدني في فهم مشكلتك بشكل أفضل.

🧠 **تحليلي الذكي لوصفك:**
• أفهم أن هذه مشكلة مهمة وتحتاج حل دقيق
• سأساعدك في حلها بسرعة وفعالية
• سأقوم بإنشاء طلب رسمي مناسب ومفصل

💡 **توقعاتي الذكية:**
• سأقوم بتحليل مشكلتك بدقة
• سأقترح عليك الحلول المناسبة
• سأتابع حالة طلبك باستمرار

🎯 **هل تريد:**
• إنشاء طلب رسمي بهذه التفاصيل؟
• الحصول على مساعدة إضافية؟
• معرفة الخطوات التالية؟

اكتب "نعم" لإنشاء الطلب!"""
    
    def generate_general_response_advanced(self, content: str, analysis: Dict, entities: Dict, context: Dict) -> str:
        """إنشاء رد عام متقدم"""
        if entities['services']:
            return f"""أفهم أن لديك مشكلة في {', '.join(entities['services'])}. 

🧠 **تحليلي الذكي:**
• سأساعدك في حل هذه المشكلة
• سأقوم بإنشاء طلب رسمي مناسب
• سأتابع حالة طلبك بدقة

هل تريد إنشاء طلب رسمي لحلها؟"""
        elif entities['problems']:
            return f"""أفهم أن لديك {', '.join(entities['problems'])}. 

🧠 **تحليلي الذكي:**
• سأساعدك في حل هذه المشكلة
• سأقوم بإنشاء طلب إصلاح مناسب
• سأتابع حالة طلبك بدقة

هل تريد مني إنشاء طلب إصلاح؟"""
        else:
            responses = [
                "أفهم، كيف يمكنني مساعدتك في هذا الأمر؟",
                "ممتاز! هل تريد تقديم طلب رسمي؟",
                "أفهم مشكلتك، هل تريد مني إنشاء طلب لك؟",
                "ممتاز! هل يمكنني مساعدتك في شيء محدد؟",
                "أفهم، هل تريد مساعدة في حل هذه المشكلة؟"
            ]
            return random.choice(responses)
    
    def handle_general_query(self, chat_room: ChatRoom, content: str, 
                           analysis: Dict, entities: Dict) -> Dict:
        """معالجة الاستفسارات العامة (النسخة القديمة للتوافق)"""
        return self.handle_general_query_advanced(chat_room, content, analysis, entities, {'conversation_phase': 'beginning'})
    
    def generate_question_response(self, content: str, analysis: Dict, entities: Dict) -> str:
        """إنشاء رد للأسئلة"""
        return f"""🤔 **سؤال ممتاز!**

أفهم سؤالك وأقدر اهتمامك. دعني أساعدك في الحصول على إجابة.

💡 **بناءً على سؤالك، أقترح:**
• كتابة "مساعدة" للحصول على معلومات عامة
• كتابة "خدمات" لمعرفة الخدمات المتاحة
• كتابة "معلومات" للحصول على تفاصيل أكثر

🔍 **أو يمكنك:**
• وصف مشكلتك بالتفصيل وسأساعدك في حلها
• كتابة "طلب" إذا كنت تريد تقديم طلب رسمي

كيف يمكنني مساعدتك بشكل أفضل؟"""
    
    def generate_urgent_response(self, content: str, analysis: Dict, entities: Dict) -> str:
        """إنشاء رد للرسائل العاجلة"""
        return f"""🚨 **أفهم أن هذه مشكلة عاجلة!**

سأقوم بمعالجة طلبك بأولوية عالية.

⚡ **للمشاكل العاجلة:**
• سأقوم بإنشاء طلب رسمي فوراً
• سأعطيك رقم تتبع للمتابعة
• سأتابع حالة طلبك باستمرار

📝 **هل تريد:**
• إنشاء طلب رسمي الآن؟
• الحصول على رقم تتبع للمتابعة؟
• معرفة الخطوات التالية؟

اكتب "نعم" لإنشاء الطلب فوراً!"""
    
    def generate_detailed_response(self, content: str, analysis: Dict, entities: Dict) -> str:
        """إنشاء رد للرسائل المفصلة"""
        return f"""📝 **شكراً لك على الشرح المفصل!**

أقدر أنك أخذت وقتك لوصف المشكلة بالتفصيل. هذا يساعدني في فهم مشكلتك بشكل أفضل.

🔍 **بناءً على وصفك:**
• أفهم أن هذه مشكلة مهمة
• سأساعدك في حلها بسرعة
• سأقوم بإنشاء طلب رسمي مناسب

💡 **هل تريد:**
• إنشاء طلب رسمي بهذه التفاصيل؟
• الحصول على مساعدة إضافية؟
• معرفة الخطوات التالية؟

اكتب "نعم" لإنشاء الطلب!"""
    
    def generate_general_response(self, content: str, analysis: Dict, entities: Dict) -> str:
        """إنشاء رد عام ذكي"""
        responses = [
            "أفهم، كيف يمكنني مساعدتك في هذا الأمر؟",
            "ممتاز! هل تريد تقديم طلب رسمي؟",
            "أفهم مشكلتك، هل تريد مني إنشاء طلب لك؟",
            "شكراً لك، هل تريد متابعة هذا الأمر؟",
            "ممتاز! هل يمكنني مساعدتك في شيء محدد؟"
        ]
        
        # اختيار رد مناسب حسب السياق
        if entities['services']:
            return f"أفهم أن لديك مشكلة في {', '.join(entities['services'])}. هل تريد إنشاء طلب رسمي لحلها؟"
        elif entities['problems']:
            return f"أفهم أن لديك {', '.join(entities['problems'])}. هل تريد مني إنشاء طلب إصلاح؟"
        else:
            return random.choice(responses)
    
    def get_conversation_history(self, chat_room: ChatRoom) -> List[Dict]:
        """الحصول على تاريخ المحادثة"""
        messages = Message.objects.filter(chat_room=chat_room).order_by('-created_at')[:10]
        
        history = []
        for message in messages:
            history.append({
                'content': message.content,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat()
            })
        
        return history
    
    def update_context(self, user_id: str, content: str, analysis: Dict):
        """تحديث سياق المحادثة"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                'last_intent': None,
                'last_entities': {},
                'conversation_count': 0,
                'preferred_services': [],
                'last_activity': timezone.now()
            }
        
        context = self.context_memory[user_id]
        context['last_intent'] = analysis['intent']
        context['last_entities'] = analysis['entities']
        context['conversation_count'] += 1
        context['last_activity'] = timezone.now()
        
        # تحديث الخدمات المفضلة
        if analysis['entities']['services']:
            for service in analysis['entities']['services']:
                if service not in context['preferred_services']:
                    context['preferred_services'].append(service)
    
    def generate_request_confirmation(self, request_obj: Request) -> str:
        """إنشاء رسالة تأكيد إنشاء الطلب"""
        return f"""✅ **تم إنشاء طلبك بنجاح!**

📋 **تفاصيل الطلب:**
• العنوان: {request_obj.title}
• رقم التتبع: **{request_obj.tracking_number}**
• الحالة: {request_obj.status.name}
• التاريخ: {request_obj.created_at.strftime('%Y-%m-%d %H:%M')}

🎯 **الخطوات التالية:**
• احتفظ برقم التتبع للمتابعة
• يمكنك متابعة طلبك في أي وقت
• ستحصل على تحديثات دورية

💡 **نصائح:**
• اكتب رقم التتبع للاستفسار عن الطلب
• اكتب "حالة طلباتي" لرؤية جميع الطلبات
• يمكنك تقديم طلب جديد في أي وقت

هل تريد مساعدة أخرى؟"""
    
    def generate_request_rejection(self) -> str:
        """إنشاء رسالة رفض إنشاء الطلب"""
        return """❌ **تم إلغاء إنشاء الطلب**

لا مشكلة! يمكنك تقديم طلب في أي وقت آخر.

💡 **يمكنك:**
• كتابة "طلب" لتقديم طلب جديد
• كتابة "مساعدة" للحصول على مساعدة
• كتابة "خدمات" لمعرفة الخدمات المتاحة

هل تريد مساعدة في شيء آخر؟"""
