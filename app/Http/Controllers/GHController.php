<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Tags;
use App\Models\Post;
class GHController extends Controller
{
    public function index(Request $request)
    {
        $tags = Tags::with(['user', 'posts'])
                    ->where('is_moderated', true)
                    ->latest()
                    ->get();

        return Inertia::render('GHShow', [
            'tags' => $tags,
        ]);
    }
}
