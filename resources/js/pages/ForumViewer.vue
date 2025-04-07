<script setup lang="ts">
import { ref, computed } from 'vue';
import { Head, router, usePage, Link } from '@inertiajs/vue3';
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import Dialog from '@/components/ui/dialog/Dialog.vue';
import DialogContent from '@/components/ui/dialog/DialogContent.vue';
import DialogHeader from '@/components/ui/dialog/DialogHeader.vue';
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue';
import DialogDescription from '@/components/ui/dialog/DialogDescription.vue';
import Button from '@/components/ui/button/Button.vue';
import Input from '@/components/ui/input/Input.vue';
import Label from '@/components/ui/label/Label.vue';

const props = defineProps({
    posts: {
        type: Array as () => Array<{
            id: number;
            title: string;
            description: string;
            image: string | null;
            created_at: string;
            is_moderated: boolean;
            user: {
                name: string;
            };
        }>,
        default: () => []
    }
});

const breadcrumbs: BreadcrumbItem[] = [
    { title: 'Форум', href: '/forum' }
];

const defaultImageUrl = 'no-image.jpg'; 
const isDialogOpen = ref(false);
const isAuthDialogOpen = ref(false);

const newPost = ref({
    title: '',
    description: '',
    image: null as File | null,
});

const page = usePage();
const isAuthenticated = computed(() => !!page.props.auth?.user);

const moderatedPosts = computed(() => props.posts.filter(post => post.is_moderated));

const handleCreatePostClick = () => {
    if (isAuthenticated.value) {
        isDialogOpen.value = true;
    } else {
        isAuthDialogOpen.value = true;
    }
};

const submitPost = async () => {
    const formData = new FormData();
    formData.append('title', newPost.value.title);
    formData.append('description', newPost.value.description);
    if (newPost.value.image) {
        formData.append('image', newPost.value.image);
    }

    try {
        await router.post('/forum', formData, {
            forceFormData: true,
            preserveScroll: true,
            onSuccess: () => {
                isDialogOpen.value = false;
                newPost.value = { title: '', description: '', image: null };
            },
            onError: (errors) => {
                console.error('Ошибка при создании поста:', errors);
            }
        });
    } catch (error) {
        console.error('Ошибка:', error);
    }
};

const handleImageError = (event: Event) => {
    const img = event.target as HTMLImageElement;
    img.src = defaultImageUrl;
    img.onerror = null;
};
</script>

<template>
    <Head title="Форум" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="flex h-full flex-1 flex-col gap-4 rounded-xl p-4">
            <Button @click="handleCreatePostClick" class="mb-4 bg-blue-600 hover:bg-blue-700">
                Создать новый пост
            </Button>
            <h1 class="text-4xl">СТАТЬИ</h1>
            
            <div class="grid auto-rows-min gap-4 mt-5 w-2/3">
                <div 
                    v-for="post in moderatedPosts" 
                    :key="post.id" 
                    class="bg-white mt-5 relative overflow-hidden rounded-xl border border-sidebar-border/70 dark:border-sidebar-border"
                >
                    <Link 
                        :href="route('post.show', { id: post.id })"
                        class="block w-full h-full"
                    >
                        <div class="w-full h-48 bg-gray-100">
                            <img 
                                :src="post.image ? `/storage/${post.image}` : defaultImageUrl" 
                                :alt="post.title" 
                                class="w-full h-full object-cover"
                                @error="handleImageError"
                            />
                        </div>

                        <div class="p-4">
                            <h2 class="text-lg font-semibold">{{ post.title }}</h2>
                            <p class="text-sm text-gray-500">{{ new Date(post.created_at).toLocaleDateString('ru-RU') }}</p>
                            <p class="text-sm mt-2">{{ post.description }}</p>
                            <button class="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                                Читать далее
                            </button>
                        </div>
                    </Link>
                </div>
            </div>

            <div v-if="posts.length === 0" class="relative min-h-[100vh] flex-1 rounded-xl border border-sidebar-border/70 dark:border-sidebar-border md:min-h-min flex items-center justify-center">
                <p class="text-gray-500">Нет доступных постов</p>
            </div>
        </div>

        <Dialog v-model:open="isDialogOpen">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Создать пост</DialogTitle>
                    <DialogDescription>
                        Заполните форму для создания нового поста
                    </DialogDescription>
                </DialogHeader>

                <form @submit.prevent="submitPost" class="space-y-4">
                    <div>
                        <Label for="title">Заголовок</Label>
                        <Input 
                            id="title" 
                            v-model="newPost.title" 
                            placeholder="Введите заголовок..." 
                            required 
                        />
                    </div>
                    <div>
                        <Label for="description">Описание</Label>
                        <Input 
                            id="description" 
                            v-model="newPost.description" 
                            placeholder="Введите описание..." 
                            required 
                        />
                    </div>
                    <div>
                        <Label for="image">Изображение</Label>
                        <Input 
                            id="image" 
                            type="file" 
                           
                            accept="image/*" 
                        />
                    </div>
                    <Button type="submit" class="w-full bg-blue-600 hover:bg-blue-700" :disabled="!newPost.title || !newPost.description">
                        Отправить
                    </Button>
                </form>
            </DialogContent>
        </Dialog>

        <Dialog v-model:open="isAuthDialogOpen">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Вход или регистрация</DialogTitle>
                    <DialogDescription>
                        Пожалуйста, войдите или зарегистрируйтесь, чтобы создать новый пост.
                    </DialogDescription>
                </DialogHeader>
                <div class="flex justify-end gap-2">
                    <Button @click="router.visit(route('login'))" class="bg-blue-600 hover:bg-blue-700">Войти</Button>
                    <Button @click="router.visit(route('register'))" class="bg-blue-600 hover:bg-blue-700">Регистрация</Button>
                </div>
            </DialogContent>
        </Dialog>
    </AppLayout>
</template>