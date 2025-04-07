<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head } from '@inertiajs/vue3';
import PlaceholderPattern from '../components/PlaceholderPattern.vue';

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'gh',
        href: '/gh',
    },
];
</script>

<template>
    <Head title="gh" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="flex h-full flex-1 flex-col gap-4 rounded-xl p-4">
            <div class="">
                <h1 class="text-2xl font-bold">Добрые истории</h1>
            </div>
            <div class="grid auto-rows-min gap-4 md:grid-cols-3">
                <div class=" h-screen w-full ">
                    adawd
                </div>
            </div>
            
        </div>
    </AppLayout>
</template>
