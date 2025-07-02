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

export const showSuccessNotification = (message: string, options?: NotificationOptions): Id => {
  return toast.success(message, { ...defaultOptions, ...options });
};

export const showErrorNotification = (message: string, options?: NotificationOptions): Id => {
  return toast.error(message, { ...defaultOptions, ...options });
};

export const showInfoNotification = (message: string, options?: NotificationOptions): Id => {
  return toast.info(message, { ...defaultOptions, ...options });
};

export const showWarningNotification = (message: string, options?: NotificationOptions): Id => {
  return toast.warn(message, { ...defaultOptions, ...options });
};

export const dismissNotification = (toastId?: Id): void => {
  if (toastId) {
    toast.dismiss(toastId);
  } else {
    toast.dismiss();
  }
};

export const useNotifications = () => {
  return {
    notifySuccess: showSuccessNotification,
    notifyError: showErrorNotification,
    notifyInfo: showInfoNotification,
    notifyWarning: showWarningNotification,
    dismiss: dismissNotification,
  };
};
