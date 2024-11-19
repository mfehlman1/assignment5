"use strict";

// Complete. 

const app = Vue.createapp({
    data() {
        return{
            posts: [],
            tags: [],
            activeTags: [],
            newContent: "",
            user: null
        };
    },

    computed: {
        filteredPosts() {
            if (this.activeTags.length === 0) {
                return this.posts;
            }
            return this.posts.filter(post => 
                post.tags.some(tag => this.activeTags.includes(tag.name))
            );
        }
    },

    methods: {
        async fetchPosts() {
            const response = await fetch("/get_posts");
            const data = await response.json();
            this.posts = data.posts;
        },
        async fetchTags() {
            const response = await fetch("/get_tags");
            const data = await response.json();
            this.tags = data.tags;
        },

        async createPost() {
            if (!this.newPostContent.trim()) {
                alert("Post must contain content");
                return;
            }
            const response = await fetch("/create_post", {
                method: "POST",
                headers: {"Content-Type": "application/json" },
                body: JSON.stringify({ content: this.newPostContent})
            });
            const data = await response.json();
            if (data.error) {
                alert(data.error);
            }
            else {
                this.newPostContent = "",
                this.fetchPosts();
                this.fetchTags();
            }
        },

        async deletePost(postId) {
            const response = await fetch('/delete_post/${postId}', {
                method: "DELETE"
            });
            const data = await response.json();
            if (data.error) {
                alert(data.error);
            }
            else {
                this.fetchPosts();
                this.fetchTags();
            }
        },

        toggleTag(tagName) {
            if (this.activeTags.includes(tagName)) {
                this.activeTags = this.activeTags.filter(tag => tag !== tagName);
            }
            else {
                this.activeTags.push(tagName);
            }
        }
    },
    mounted() {
        this.fetchPosts();
        this.fetchTags();
    }
});

app.component("post-list", {
    props: ["posts"],
    template: "#post-list-template"
});

app.component("tag-list", {
    props: ["tags", "activeTags"],
    template: "#tag-list-template"
});

app.component("post-creation", {
    props:["newPostContent"],
    template: "#post-creation-template",
    emits: ["on-create"]
});

app.mount("#app");