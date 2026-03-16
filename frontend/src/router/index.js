import {
    createRouter,
    createWebHistory
}from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import BehaviorFlow from '../views/BehaviorFlow.vue'
import UserAnalysis from '../views/UserAnalysis.vue'
import Prediction from '../views/Prediction.vue'
import Comparison from '../views/Comparison.vue'

const routes = [
    {
        path: '/',
        redirect: '/dashboard',
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
    },
    {
        path: '/behavior-flow',
        name: 'BehaviorFlow',
        component: BehaviorFlow,
    },
    {
        path: '/user-analysis',
        name: 'UserAnalysis',
        component: UserAnalysis,
    },
    {
        path: '/prediction',
        name: 'Prediction',
        component: Prediction,
    },
    {
        path: '/comparison',
        name: 'Comparison',
        component: Comparison,
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router