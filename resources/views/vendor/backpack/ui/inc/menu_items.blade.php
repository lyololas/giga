{{-- This file is used for menu items by any Backpack v6 theme --}}
<li class="nav-item"><a class="nav-link" href="{{ backpack_url('dashboard') }}"><i class="la la-home nav-icon"></i> {{ trans('backpack::base.dashboard') }}</a></li>

<x-backpack::menu-item title="Posts" icon="la la-question" :link="backpack_url('posts')" />
<x-backpack::menu-item title="Comments" icon="la la-question" :link="backpack_url('comments')" />
<x-backpack::menu-item title="Good histories" icon="la la-question" :link="backpack_url('good-histories')" />
<x-backpack::menu-item title="Users" icon="la la-question" :link="backpack_url('users')" />
<x-backpack::menu-item title="Tags" icon="la la-question" :link="backpack_url('tags')" />
<x-backpack::menu-item title="Questions and answers" icon="la la-question" :link="backpack_url('questions-and-answers')" />