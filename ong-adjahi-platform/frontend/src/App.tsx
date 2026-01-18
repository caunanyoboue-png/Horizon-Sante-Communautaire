import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Login from './pages/auth/Login'
import Dashboard from './pages/dashboard/Dashboard'
import PatientsList from './pages/patients/PatientsList'
import PatientDetail from './pages/patients/PatientDetail'
import PregnanciesList from './pages/cpn/PregnanciesList'
import PregnancyDetail from './pages/cpn/PregnancyDetail'
import Layout from './components/layout/Layout'
import { useAuthStore } from './store/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Private routes */}
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="patients" element={<PatientsList />} />
            <Route path="patients/:id" element={<PatientDetail />} />
            <Route path="cpn" element={<PregnanciesList />} />
            <Route path="cpn/:id" element={<PregnancyDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
      
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App
