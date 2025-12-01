import { toast } from "sonner";
import { CircleX, MailX } from "lucide-react";

export function onError(errors: any) {
    if (errors.username) {
        toast.error(errors.username.message, { 
            position: 'bottom-right', 
            icon: <CircleX/>,
            style: { 
                background: "#448094ff",
                color: "#ffffff",
                border: "#448094ff"
            }
        });
    }
    if (errors.email) {
        toast.error(errors.email.message, { 
            position: 'bottom-right', 
            icon: <MailX/>,
            style: { 
                background: "#448094ff",
                color: "#ffffff",
                border: "#448094ff"
            } 
        });
    }
    if (errors.password) {
        toast.error(errors.password.message, { 
            position: 'bottom-right', 
            icon: <CircleX/>,
            style: { 
                background: "#448094ff",
                color: "#ffffff",
                border: "#448094ff"
            }
        });
    }
}