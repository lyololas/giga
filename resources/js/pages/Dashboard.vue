<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head, router } from '@inertiajs/vue3';
import { ref } from 'vue';

const props = defineProps({
    posts: {
        type: Array,
        default: () => []
    },
    histories: {
        type: Array,
        default: () => []
    },
    totalHistories: {
        type: Number,
        default: 0
    },
    totalPosts: {
        type: Number,
        default: 0
    }
});

const breadcrumbs: BreadcrumbItem[] = [
    { title: 'Dashboard', href: '/dashboard' },
];

// FAQ data
const faqs = ref([
    {
        question: 'Гарантируете ли вы анонимность для обратившихся?',
        answer: 'Да, все данные строго конфиденциальны. Мы не разглашаем имена и истории без согласия участников.',
    },
    {
        question: 'Кто может обратиться за помощью?',
        answer: 'Любой человек, который нуждается в поддержке, может обратиться за помощью.',
    },
    {
        question: 'Как я могу помочь вашему проекту?',
        answer: 'Вы можете помочь, став волонтером, делая пожертвования или распространяя информацию о проекте.',
    },
    {
        question: 'Зачем это нужно?',
        answer: 'Снимает барьеры (люди быстрее решаются на обращение), экономит время сотрудников (меньше рутинных вопросов), укрепляет доверие (прозрачность и подробные ответы).',
    },
]);

const categories = ref([
    {
        name: 'СВОИ Новости',
        icon: '/images/news-icon.png',
        count: props.totalPosts,
    },
    {
        name: 'СВОИ Обсуждения',
        icon: '/images/discussions-icon.png',
        count: props.totalHistories,
    },
    {
        name: 'СВОИ Истории',
        icon: '/images/stories-icon.png',
        count: props.totalHistories,
    },
    {
        name: 'СВОИ Вопросы',
        icon: '/images/faq-icon.png',
        count: faqs.value.length,
    },
]);

const openFaqIndex = ref<number | null>(null);

const toggleFaq = (index: number) => {
    openFaqIndex.value = openFaqIndex.value === index ? null : index;
};
</script>

<template>
    <Head title="СВОИ - Потому что помощь не бывает чужой" />
    
    <AppLayout :breadcrumbs="breadcrumbs">
        <!-- Hero Section -->
        <section 
            class="relative h-[566px] bg-gray-900"
            style="background: url('image.svg') no-repeat center center; background-size: cover;"
        >
            <div class="absolute inset-0 bg-black/50"></div>
            <div class="relative z-10 h-full flex flex-col justify-center items-center text-center px-6">
                <h1 class="text-5xl font-bold text-white mb-4">СВОИ</h1>
                <p class="text-4xl text-white">Потому что помощь не бывает чужой</p>
                
                <div class="mt-12 w-full max-w-4xl">
                    <!-- Filters -->
                    <div class="flex flex-wrap justify-center gap-4 mb-6">
                        <button class="px-6 py-3 bg-white rounded-2xl border border-gray-300 font-semibold">
                            с Ответом
                        </button>
                        <button class="px-6 py-3 bg-white rounded-2xl border border-gray-300 font-semibold">
                            Вопрос - Ответ
                        </button>
                        <button class="px-6 py-3 bg-white rounded-2xl border border-gray-300 font-semibold">
                            Залайканные
                        </button>
                        <button class="px-6 py-3 bg-white rounded-2xl border border-gray-300 font-semibold">
                            Популярные
                        </button>
                    </div>
                    
                    <!-- Search -->
                    <div class="bg-white p-4 rounded-2xl">
                        <div class="flex gap-4">
                            <input 
                                type="text" 
                                placeholder="Введите запрос"
                                class="flex-1 px-4 py-3 bg-gray-50 rounded-2xl"
                            >
                            <button class="px-6 py-3 bg-emerald-600 text-white font-semibold rounded-2xl">
                                Найти
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Categories Section -->
        <section class="container mx-auto px-4 py-16">
            <h2 class="text-5xl font-bold mb-8">Категории</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div 
                    v-for="(category, index) in categories" 
                    :key="index"
                    class="flex items-center gap-4 p-4 hover:bg-gray-50 rounded-xl transition-colors"
                >
                    <img 
                        :src="category.icon" 
                        :alt="category.name"
                        class="w-24 h-24 object-contain rounded-2xl"
                    >
                    <div>
                        <h3 class="text-xl font-semibold">
                            
                        </h3>
                        <p class="text-sm text-gray-500">{{ category.count }} {{ category.name.split(' ')[1].toLowerCase() }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- News Section (Forum Posts) -->
        <section class="container mx-auto px-4 py-16">
            <div class="flex justify-between items-center mb-8">
                <h2 class="text-5xl font-bold">Новости</h2>
                <a :href="route('forum.index')" class="px-6 py-3 bg-gray-100 text-gray-600 font-semibold rounded-2xl">
                    Все
                </a>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div 
                    v-for="post in posts.slice(0, 3)" 
                    :key="post.id"
                    class="bg-white rounded-[32px] overflow-hidden shadow-sm"
                >
                    <img 
                        v-if="post.image"
                        :src="'/storage/' + post.image" 
                        :alt="post.title"
                        class="w-full h-48 object-cover"
                    >
                    <div v-else class="w-full h-48 bg-gray-200 flex items-center justify-center">
                        <span class="text-gray-500">No image</span>
                    </div>
                    <div class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <div class="flex items-center gap-2">
                                <div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                                    <span class="text-gray-500">{{ post.user.name.charAt(0) }}</span>
                                </div>
                                <div>
                                    <p class="font-medium">{{ post.user.name }}</p>
                                </div>
                            </div>
                            <a :href="route('forum.show', { id: post.id })" class="px-4 py-2 bg-gray-100 text-gray-600 text-sm font-semibold rounded-2xl">
                                Подробнее
                            </a>
                        </div>
                        <h3 class="text-2xl font-bold uppercase">{{ post.title }}</h3>
                        <p class="mt-2 text-lg line-clamp-2">{{ post.description }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Discussions Section (Good Histories) -->
        <section class="container mx-auto px-4 py-16">
            <div class="flex justify-between items-center mb-8">
                <h2 class="text-5xl font-bold">Обсуждения</h2>
                <a :href="route('gh.index')" class="px-6 py-3 bg-gray-100 text-gray-600 font-semibold rounded-2xl">
                    Все
                </a>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div 
                    v-for="history in histories.slice(0, 3)" 
                    :key="history.id"
                    class="bg-white rounded-[32px] overflow-hidden shadow-sm"
                >
                    <img 
                        v-if="history.image"
                        :src="'/storage/' + history.image" 
                        :alt="history.title"
                        class="w-full h-48 object-cover"
                    >
                    <div v-else class="w-full h-48 bg-gray-200 flex items-center justify-center">
                        <span class="text-gray-500">No image</span>
                    </div>
                    <div class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <div class="flex items-center gap-2">
                                <div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                                    <span class="text-gray-500">{{ history.user.name.charAt(0) }}</span>
                                </div>
                                <div>
                                    <p class="font-medium">{{ history.user.name }}</p>
                                </div>
                            </div>
                            <a :href="route('gh.show', { id: history.id })" class="px-4 py-2 bg-gray-100 text-gray-600 text-sm font-semibold rounded-2xl">
                                Подробнее
                            </a>
                        </div>
                        <h3 class="text-2xl font-bold uppercase">{{ history.title }}</h3>
                        <p class="mt-2 text-lg line-clamp-2">{{ history.description }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- FAQ Section -->
        <section class="container mx-auto px-4 py-16">
            <h2 class="text-5xl font-bold mb-8">Часто задаваемые вопросы</h2>
            
            <div class="space-y-4">
                <div 
                    v-for="(faq, index) in faqs" 
                    :key="index"
                    class="bg-white rounded-[32px] overflow-hidden"
                >
                    <div 
                        class="flex justify-between items-center p-6 cursor-pointer"
                        @click="toggleFaq(index)"
                    >
                        <h3 class="text-2xl font-semibold">{{ faq.question }}</h3>
                        <div class="w-12 h-12 flex items-center justify-center bg-gray-100 rounded-2xl">
                            <span :class="{'rotate-180': openFaqIndex === index}">▼</span>
                        </div>
                    </div>
                    <div 
                        v-if="openFaqIndex === index"
                        class="p-6 bg-gray-50"
                    >
                        <p class="text-lg">{{ faq.answer }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="container mx-auto px-4 py-16">
            <div class="bg-white rounded-[32px] p-12 text-center">
                <h2 class="text-4xl font-bold mb-4">Остались вопросы?</h2>
                <p class="text-lg mb-8">Перейдите в телеграм!</p>
                <button class="px-6 py-4 bg-emerald-600 text-white font-semibold rounded-2xl">
                    Подробнее
                </button>
            </div>
        </section>

        <!-- Footer -->
        <footer class="bg-white py-8">
            <div class="container mx-auto px-4">
                <div class="flex flex-col items-center">
                    <div class="flex gap-8 font-semibold mb-4">
                        <a href="#">О нас</a>
                        <a href="#">Контакты</a>
                        <a href="#">Помощь</a>
                    </div>
                    <div class="flex gap-8 text-sm">
                        <span class="text-black">©2024 "СВОИ". Все права защищены</span>
                        <a href="#" class="text-blue-600">Политика конфиденциальности</a>
                        <a href="#" class="text-blue-600">Пользовательское согласование</a>
                    </div>
                </div>
            </div>
        </footer>
    </AppLayout>
</template>

<style scoped>
.rotate-180 {
    transform: rotate(180deg);
    transition: transform 0.2s ease;
}
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>