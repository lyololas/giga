<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head } from '@inertiajs/vue3';
import { Button } from '@/components/ui/button';

const props = defineProps<{
    history: any;
}>();

const breadcrumbs: BreadcrumbItem[] = [
    { title: 'Good Histories', href: '/gh' },
    { title: props.history.title, href: `/gh/${props.history.id}` }
];
</script>

<template>
    <Head :title="history.title" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="container mx-auto px-4 py-8">
            <div class="max-w-3xl mx-auto">
                <img 
                    :src="history.image" 
                    :alt="history.title" 
                    class="w-full h-96 object-cover rounded-lg mb-8"
                />
                <h1 class="text-4xl font-bold mb-4">{{ history.title }}</h1>
                <div class="flex flex-wrap gap-2 mb-6">
                    <span 
                        v-for="tag in history.tags" 
                        :key="tag.id"
                        class="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
                    >
                        {{ tag.name }}
                    </span>
                </div>

                <!-- Full Story Content -->
                <div class="prose max-w-none mb-8">
                    <p class="whitespace-pre-line">{{ history.description }}</p>
                </div>

                <!-- Back Button -->
                <Button 
                    @click="$inertia.visit('/gh')"
                    class="bg-[#088B64] hover:bg-[#077a56] text-white"
                >
                    Назад к историям
                </Button>
            </div>
        </div>
    </AppLayout>
</template>