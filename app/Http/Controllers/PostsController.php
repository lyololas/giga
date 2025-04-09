<?php

namespace App\Http\Controllers;

use App\Models\Post;
use App\Models\Comments;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Inertia\Inertia;

class PostsController extends Controller
{
    public function index(Request $request)
    {
        $posts = Post::with(['user', 'comments'])
                    ->where('is_moderated', true)
                    ->latest()
                    ->get();

        return Inertia::render('ForumViewer', [
            'posts' => $posts,
        ]);
    }

    public function show($id)
    {
        $post = Post::with(['user', 'comments.user']) 
                  ->findOrFail($id);

        $comments = $post->comments()
                       ->with('user')
                       ->get();

        return Inertia::render('ForumShow', [
            'post' => $post,
            'comments' => $comments,
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'description' => 'required|string',
            'image' => 'nullable|image|mimes:jpeg,png,jpg|max:2048',
        ]);

        $post = new Post();
        $post->title = $validated['title'];
        $post->description = $validated['description'];
        $post->user_id = Auth::id();

        if ($request->hasFile('image')) {
            $path = $request->file('image')->store('posts', 'public');
            $post->image = $path;
        }

        $post->save();

        return redirect()->route('forum.index')
            ->with('success', 'Post created successfully!');
    }

    public function storeComment(Request $request, $postId)
    {
        $validated = $request->validate([
            'content' => 'required|string|max:1000',
        ]);

        $post = Post::findOrFail($postId);

        $comment = new Comments();
        $comment->content = $validated['content'];
        $comment->user_id = Auth::id();
        $comment->post_id = $post->id;
        $comment->save();

        return redirect()->route('forum.show', $post->id)
            ->with('success', 'Comment added successfully');
    }
}