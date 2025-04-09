<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head } from '@inertiajs/vue3';

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'qrcode',
        href: '/qrcode',
    },
];
</script>

<template>
    <Head title="QR Code" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="w-full h-full grid grid-cols-5 gap-4">
            <!-- Left Column: QR Code -->
            <div class="col-span-2 flex justify-center items-center bg-gray-100 rounded-lg p-4">
                <div class="w-64 h-64 bg-gray-300 flex justify-center items-center rounded-lg">
                    <img src='qr.png'/>
                </div>
            </div>

            <!-- Right Column: Image -->
            <div class="col-span-3 flex justify-center items-center bg-gray-100 rounded-lg p-4">
                <img
                    src="Group 4.svg"
                    alt="Placeholder Image"
                    class="rounded-lg object-cover"
                />
            </div>
        </div>
    </AppLayout>
</template>
