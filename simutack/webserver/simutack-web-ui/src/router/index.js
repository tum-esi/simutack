import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../views/Home.vue') // Allow lazy loading
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue') // Allow lazy loading
    },
    {
        path: '/sensors',
        name: 'Sensors',
        component: () => import('../views/Sensors.vue') // Allow lazy loading
    },
    {
        path: '/autopilot',
        name: 'Autopilot',
        component: () => import('../views/Autopilot.vue') // Allow lazy loading
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue') // Allow lazy loading
    },
]

const router = new VueRouter({
    // mode: 'history',
    routes: routes
})

export default router
