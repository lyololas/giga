<template>
    <Head :title="post.title" />
    <AppLayout :breadcrumbs="breadcrumbs">
        <!-- Секция поста (без изменений) -->
        <div class="bg-white p-6 rounded-lg shadow-md mb-6">
            <h1 class="text-2xl font-bold mb-2">{{ post.title }}</h1>
            <p class="text-gray-600 mb-4">{{ post.description }}</p>
            
            <div class="mt-4">
                <img 
                    v-if="post.image" 
                    :src="postImageUrl" 
                    :alt="post.title" 
                    class="w-full h-auto rounded-lg object-cover max-h-96"
                    @error="handleImageError"
                />
                <div v-else class="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                    <span class="text-gray-400">Нет изображения</span>
                </div>
            </div>
            <div class="flex items-center text-sm text-gray-500 mb-4">
                <span class="mr-4">Автор: {{ post.user.name }}</span>
                <span>Опубликовано: {{ formatDate(post.created_at) }}</span>
            </div>
        </div>

        <!-- Секция комментариев -->
        <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold">Комментарии ({{ sortedComments.length }})</h2>
                <button 
                    v-if="isAuthenticated"
                    @click="scrollToCommentForm"
                    class="text-sm text-blue-500 hover:text-blue-700"
                >
                    Добавить комментарий
                </button>
            </div>

            <!-- Список комментариев -->
            <div class="space-y-4" v-if="sortedComments.length > 0">
                <div 
                    v-for="comment in sortedComments" 
                    :key="comment.id" 
                    class="flex items-start space-x-4 group"
                >
                    <!-- Бейдж доверенного пользователя -->
                    <div class="flex-shrink-0 relative">
                        <div 
                            class="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center transition-all"
                            :class="{
                                'ring-2 ring-blue-500': comment.user.is_trusted,
                                'group-hover:ring-2 group-hover:ring-blue-200': !comment.user.is_trusted
                            }"
                        >
                            <span class="text-gray-600">{{ comment.user.name.charAt(0) }}</span>
                        </div>
                        <span 
                            v-if="comment.user.is_trusted"
                            class="absolute -top-1 -right-1 h-5 w-5 bg-blue-500 rounded-full flex items-center justify-center shadow-sm"
                            title="Доверенный пользователь"
                        >
                            <svg class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                            </svg>
                        </span>
                    </div>

                    <!-- Содержание комментария -->
                    <div class="flex-1">
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <div class="flex items-center gap-2">
                                <span class="font-semibold">{{ comment.user.name }}</span>
                                <span 
                                    v-if="comment.user.is_trusted"
                                    class="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full flex items-center gap-1"
                                >
                                    <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                    </svg>
                                    Доверенный участник
                                </span>
                            </div>
                            <p class="text-gray-700 mt-1">{{ comment.content }}</p>
                        </div>
                        <div class="text-sm text-gray-500 mt-2">
                            {{ formatDate(comment.created_at) }}
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
                Пока нет комментариев. Будьте первым!
            </div>

            <!-- Форма комментария -->
            <form 
                @submit.prevent="handleAddComment" 
                class="mt-6"
                ref="commentForm"
            >
                <label for="comment" class="block text-sm font-medium text-gray-700 mb-1">
                    Добавьте ваш комментарий
                    <span v-if="isAuthenticated" class="text-gray-400 text-xs">
                        (Вы вошли как {{ page.props.auth.user.name }})
                    </span>
                </label>
                <textarea
                    id="comment"
                    v-model="newComment"
                    placeholder="Напишите ваш комментарий..."
                    class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    :disabled="!isAuthenticated"
                ></textarea>
                <div class="flex justify-end mt-3">
                    <button
                        type="submit"
                        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                        :disabled="!isAuthenticated || !newComment.trim()"
                    >
                        Отправить
                    </button>
                </div>
            </form>
        </div>

        <!-- Диалог авторизации -->
        <Dialog v-model:open="isAuthDialogOpen">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Вход или регистрация</DialogTitle>
                    <DialogDescription>
                        Пожалуйста, войдите или зарегистрируйтесь, чтобы оставить комментарий.
                    </DialogDescription>
                </DialogHeader>
                <div class="flex justify-end gap-2">
                    <Button @click="router.visit(route('login'))">Войти</Button>
                    <Button @click="router.visit(route('register'))">Регистрация</Button>
                </div>
            </DialogContent>
        </Dialog>
    </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head, router, usePage } from '@inertiajs/vue3';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog'; 
import { Button } from '@/components/ui/button'; 

// Типы
type User = {
    id: number;
    name: string;
    is_trusted: boolean;
};

type Comment = {
    id: number;
    content: string;
    created_at: string;
    is_approved: boolean;
    user: User;
};

type Post = {
    id: number;
    title: string;
    description: string;
    theme?: string;
    image: string | null;
    created_at: string;
    is_moderated: boolean;
};

const props = defineProps<{
    post: Post;
    comments: Comment[];
}>();

const breadcrumbs: BreadcrumbItem[] = [
    { title: 'Форум', href: '/forum' },
    { title: props.post.title, href: route('post.show', { id: props.post.id }) }
];

const newComment = ref('');
const isAuthDialogOpen = ref(false);
const commentForm = ref<HTMLFormElement | null>(null);
const page = usePage();
const isAuthenticated = computed(() => !!page.props.auth?.user);
const postImageUrl = computed(() => props.post.image 
    ? `/storage/${props.post.image}`
    : '/images/no-image.jpg'
);

const sortedComments = computed(() => {
    if (!props.comments) return [];
    
    return [...props.comments].sort((a, b) => {
        const aTrusted = a.user?.is_trusted ? 1 : 0;
        const bTrusted = b.user?.is_trusted ? 1 : 0;
        
        if (aTrusted !== bTrusted) return bTrusted - aTrusted;
        
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
});

const formatDate = (dateString: string): string => {
    const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    };
    return new Date(dateString).toLocaleDateString('ru-RU', options);
};

const handleImageError = (event: Event): void => {
    const img = event.target as HTMLImageElement;
    img.src = '/no-image.jpg';
};

const scrollToCommentForm = (): void => {
    commentForm.value?.scrollIntoView({ behavior: 'smooth' });
};

const handleAddComment = (): void => {
    if (!isAuthenticated.value) {
        isAuthDialogOpen.value = true;
        return;
    }
    addComment();
};

const addComment = async (): Promise<void> => {
    try {
        await router.post(route('posts.comment.store', { post: props.post.id }), {
            content: newComment.value,
        }, {
            preserveScroll: true,
            onSuccess: () => {
                newComment.value = '';
                scrollToCommentForm();
            }
        });
    } catch (error) {
        console.error('Ошибка при отправке комментария:', error);
    }
};

onMounted(() => {
    if (window.location.hash === '#comment') {
        const textarea = document.getElementById('comment');
        textarea?.focus();
    }
});
</script>

<style scoped>
.trusted-badge {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}
</style>