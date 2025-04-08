<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head, router } from '@inertiajs/vue3';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { ref } from 'vue';

const props = defineProps<{
    currentHistory: any;
    allTags: any[];
    totalHistories: number;
}>();

const breadcrumbs: BreadcrumbItem[] = [
    { title: 'Good Histories', href: '/good-histories' }
];

const currentHistory = ref(props.currentHistory);
const loading = ref(false);

const loadNextHistory = async () => {
    loading.value = true;
    try {
        const response = await router.get('/good-histories/random');
        currentHistory.value = response.props.currentHistory;
    } catch (error) {
        console.error('Error loading next history:', error);
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <Head title="Good Histories" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="container mx-auto px-4 py-8">
            <!-- Hero Section -->
            <Card class="mb-8" v-if="currentHistory">
                <CardHeader>
                    <img 
                        :src="currentHistory.image" 
                        alt="Featured History" 
                        class="w-full h-64 object-cover rounded-lg"
                    />
                </CardHeader>
                <CardContent class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <CardTitle class="text-3xl font-bold">Истории добрых дел</CardTitle>
                        <CardDescription>{{ totalHistories }} историй доступно</CardDescription>
                    </div>
                   
                </CardContent>
            </Card>

            <!-- Tags Section -->
            <div class="mb-8">
                <h2 class="text-xl font-semibold mb-4">Популярные теги</h2>
                <div class="flex flex-wrap gap-2">
                    <span 
                        v-for="tag in allTags" 
                        :key="tag.id"
                        class="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800 cursor-pointer hover:bg-gray-200"
                    >
                        {{ tag.name }}
                    </span>
                </div>
            </div>

            <div v-if="currentHistory">
                <p class="text-gray-500 mb-2" v-if="currentHistory.author">Автор: {{ currentHistory.author }}</p>
                <Card>
                    <CardHeader>
                        <CardTitle class="text-2xl">{{ currentHistory.title }}</CardTitle>
                        <div class="flex flex-wrap gap-2 mt-2">
                            <span 
                                v-for="tag in currentHistory.tags" 
                                :key="tag.id"
                                class="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
                            >
                                {{ tag.name }}
                            </span>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <p class="text-gray-600 mb-4">{{ currentHistory.description }}</p>
                        <Button class="bg-[#088B64] hover:bg-[#077a56] text-white">
                            Читать полностью
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <div v-else class="text-center py-12">
                <p class="text-gray-500">Нет доступных историй</p>
            </div>
        </div>
    </AppLayout>
</template>