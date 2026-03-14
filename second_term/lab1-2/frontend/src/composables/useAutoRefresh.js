import { onBeforeUnmount, watch } from "vue";

export function useAutoRefresh(callback, delayRef, enabledRef) {
  let timerId = null;

  const clearTimer = () => {
    if (timerId) {
      window.clearInterval(timerId);
      timerId = null;
    }
  };

  watch(
    [delayRef, enabledRef],
    ([delay, enabled]) => {
      clearTimer();
      if (!enabled || !delay || delay <= 0) {
        return;
      }

      timerId = window.setInterval(() => {
        if (!document.hidden) {
          callback();
        }
      }, delay);
    },
    { immediate: true },
  );

  onBeforeUnmount(clearTimer);
}
