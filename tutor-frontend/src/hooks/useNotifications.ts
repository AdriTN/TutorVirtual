import { toast, ToastOptions, Id } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface NotificationOptions extends ToastOptions {}

const defaultOptions: NotificationOptions = {
  position: "top-right",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
  theme: "light",
};

export const useNotifications = () => {
  const notifySuccess = (message: string, options?: NotificationOptions): Id => {
    return toast.success(message, { ...defaultOptions, ...options });
  };

  const notifyError = (message: string, options?: NotificationOptions): Id => {
    return toast.error(message, { ...defaultOptions, ...options });
  };

  const notifyInfo = (message: string, options?: NotificationOptions): Id => {
    return toast.info(message, { ...defaultOptions, ...options });
  };

  const notifyWarning = (message: string, options?: NotificationOptions): Id => {
    return toast.warn(message, { ...defaultOptions, ...options });
  };

  const dismiss = (toastId?: Id): void => {
    if (toastId) {
      toast.dismiss(toastId);
    } else {
      toast.dismiss();
    }
  };

  return {
    notifySuccess,
    notifyError,
    notifyInfo,
    notifyWarning,
    dismiss,
  };
};
