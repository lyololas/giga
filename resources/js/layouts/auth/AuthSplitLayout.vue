<script setup lang="ts">
import AppLogoIcon from '@/components/AppLogoIcon.vue';
import { Link, usePage } from '@inertiajs/vue3';

const page = usePage();
const name = page.props.name;
const quote = page.props.quote;

defineProps<{
    title?: string;
    description?: string;
}>();
</script>

<template>
    <div class="relative grid h-dvh flex-col items-center justify-center px-8 sm:px-0 lg:max-w-none lg:grid-cols-2 lg:px-0">
        <div class="lg:p-8">
            <div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
                <div class="rounded-lg border bg-card p-6 shadow-sm">
                    <div class="flex flex-col space-y-2 text-center">
                        <h1 class="text-xl font-medium tracking-tight" v-if="title">{{ title }}</h1>
                        <p class="text-sm text-muted-foreground" v-if="description">{{ description }}</p>
                    </div>
                    <slot />
                </div>
            </div>
        </div>
        <div class="relative hidden h-full flex-col p-10 text-white lg:flex lg:order-last">
            <div class="absolute inset-0 flex items-center justify-center w-2/3">
                <!-- Здесь можно разместить ваше изображение -->
                <img src="register.svg" class=""/>
            </div>
        </div>
    </div>
</template>