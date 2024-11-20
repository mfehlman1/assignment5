"use strict";

// Complete.  

const app = Vue.createApp({
    data() {
        return{
            posts: [],
            tags: [],
            activeTags: [],
            newPostContent: "",
            user: null
        };
    },

//function for handling the filtering computation based on active tags
    computed: {
        filteredPosts() {
            if (this.activeTags.length === 0) {
                return this.posts;
            }
            return this.posts.filter(post => {
                const postTags = post.tags || []; 
                return postTags.some(tag => this.activeTags.includes(tag));
            });
        }
    },


    methods: {
//fetches the user info from the backend
        async fetchUserInfo() {
            try {
                const response = await fetch("/topical/user_info");
                if (!response.ok) {
                    console.error("Failed to fetch user info");
                    return;
                }
                const data = await response.json();
                this.user = data.user_id;
                console.log("User-Id: ", this.user);
            }
            catch (error) {
                console.error("Error fetching user info:", error)
            }
        },

//fetchs posts from the backend
        async fetchPosts() {
            const response = await fetch("/topical/get_posts");
            if (!response.ok) {
                console.error("Failed to fetch posts");
                return;
            }
            const data = await response.json();
            this.posts = data.posts.map(post => ({
                ...post,
                tags: post.tags || [] 
            }));
            console.log("Fetched Posts:", this.posts);
        },

//fetches tags from the backend
        async fetchTags() {
            const response = await fetch("/topical/get_tags");
            if (!response.ok) {
                console.error("Failed to fetch tags");
                return;
            }
            const data = await response.json();
            this.tags = data.tags;
        },

//creates a new post by placing "content" in newPostContent
        async createPost() {
            if (!this.newPostContent.trim()) {
                alert("Post must contain content");
                return;
            }
            try {
                const response = await fetch("/topical/create_post", {
                    method: "POST",
                    headers: {"Content-Type": "application/json" },
                    body: JSON.stringify({ content: this.newPostContent })
                });
                const data = await response.json();
                if (data.error) {
                    alert(data.error);
                } else {
                    this.newPostContent = "";
                    this.fetchPosts();
                    this.fetchTags();
                }
            }  catch (error) {
                    console.error("Error creating post:", error);
                }
        },

//deletes a post based on the user post Id

        async deletePost(postId) {
            try {
                const response = await fetch(`/topical/delete_post/${postId}`, {
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
            } 
            catch(error) {
                console.error("Error deleting post: ", error);
            }
            
        },


//toggles the selection of a tag based on the current active tags
        toggleTag(tagName) {
            if (this.activeTags.includes(tagName)) {
                this.activeTags = this.activeTags.filter(tag => tag !== tagName);
            }
            else {
                this.activeTags.push(tagName);
            }
            console.log("Updated Active Tags:", this.activeTags);
        }
    },

    //fetches the initial data
    mounted() {
        this.fetchUserInfo();
        this.fetchPosts();
        this.fetchTags();
    },
});

//component for displaying the list of posts
app.component("post-list", {
    props: ["posts"],
    template: "#post-list-template",
    emits: ["on-delete"]
});

//component for displaying the list of tags
app.component("tag-list", {
    props: ["tags", "activeTags"],
    template: "#tag-list-template",
    emits: ["on-toggle"]
});

//component for handling the creation of a post
app.component("post-creation", {
    props:["newPostContent"],
    template: "#post-creation-template",
    emits: ["on-create"]
});

app.mount("#app");