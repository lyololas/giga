<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';
import { Head } from '@inertiajs/vue3';

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'qa',
        href: '/qa',
    },
];
</script>

<template>
    <Head title="gh" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="flex h-full flex-1 flex-col gap-4 rounded-xl p-4">
            <div class="">
                <div class="">
                <div class="rounded-lg bg-white">
                    <div class="rounded-lg p-5">
                        <img src="https://s3-alpha-sig.figma.com/img/9d9d/10ed/d9b91f71781ec49c1da9ca979f4e544d?Expires=1745193600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=kdePU46DC0cdJFDHEQ3BnzHbe-Bf-ZzMFKjlG88C3jNc1RtA0XJfCYpCTC9-fnlIfLUNfnHQBJ4bKg5LRHjnCwazYnpuF91~nO0ckPcgF9FAX4mkrrk8OmQvXvEVvH4NtoFiREv-kBksiVWYLAEQqVs54bWl1v3dTEqmwGMkqjWkLGyu-R7jT~2LpD4FZdfqFDH~0kqYHh55cs~lfjb0gLvNRqsoSinx01B1PsIl~n9g4ZGB2RBsW7sZPueeN8NZZbSGW~IIhiOG9J58YRt8Abc4wcjBg~yXzJpxbKV58fDFf7OZjLRa40N3A~NYnPwfwZ4Ikwqsf~tck3Q0wkKc6g__" 
                        alt="" class="w-full h-56 object-none rounded-lg ">
                        
                    </div>
                    <div class="p-5 flex justify-items-stretch">
                        <div class="">
                            <h1 class="font-bold text-4xl">Истории</h1>
                            <p>130 истории</p>
                        </div>
                        <div class="w-full">

                        </div>
                        <button type="button" class="text-white bg-[#088B64] hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 w-96">Подробнее о теме</button>
                    </div>
                    
                </div>
                <div>
                    теги
                </div>
                <div class="p-5">
                    <h1 class="text-4xl font-bold">Все истории</h1>
                    <div class="bg-white w-full rounded-lg p-5">
                            <h1 class="font-semibold text-2xl">Как я вернусля домой</h1>
                            <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Consequatur ex libero qui quas, ullam, deleniti corrupti voluptates odit cum pariatur nulla repudiandae aut quidem id quaerat incidunt laboriosam sint commodi.</p>
                            <button type="button" class="text-white bg-[#088B64] hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2">Читать полностью</button>
                    </div>
                </div>
                <div>
                    
                </div>
            </div>
               
            </div>
            
        </div>
    </AppLayout>
</template>
