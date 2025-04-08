<?php

use Illuminate\Support\Facades\Route;

// --------------------------
// Custom Backpack Routes
// --------------------------
// This route file is loaded automatically by Backpack\CRUD.
// Routes you generate using Backpack\Generators will be placed here.

Route::group([
    'prefix' => config('backpack.base.route_prefix', 'admin'),
    'middleware' => array_merge(
        (array) config('backpack.base.web_middleware', 'web'),
        (array) config('backpack.base.middleware_key', 'admin')
    ),
    'namespace' => 'App\Http\Controllers\Admin',
], function () { // custom admin routes
    Route::crud('posts', 'PostsCrudController');
    Route::crud('comments', 'CommentsCrudController');
    Route::crud('good-histories', 'GoodHistoriesCrudController');
    Route::crud('users', 'UsersCrudController');
    Route::crud('tags', 'TagsCrudController');
    Route::crud('questions-and-answers', 'QuestionsAndAnswersCrudController');
}); // this should be the absolute last line of this file

/**
 * DO NOT ADD ANYTHING HERE.
 */
