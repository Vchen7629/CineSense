import { Navigate, Outlet } from "react-router";
import { useAuth } from "@/shared/hooks/useAuth";

// Wrapper component for protected routes
export const ProtectedRoute = ({ children }: { children?: React.ReactNode }) => {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return null  
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return children ? <>{children}</> : <Outlet />
}