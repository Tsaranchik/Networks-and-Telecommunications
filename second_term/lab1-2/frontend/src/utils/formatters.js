export function formatNumber(value, locale = "ru") {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: Number.isInteger(Number(value)) ? 0 : 2,
    maximumFractionDigits: 4,
  }).format(Number(value));
}

export function formatDate(value, locale = "ru-RU") {
  if (!value) {
    return "—";
  }
  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

export function formatTime(value, locale = "ru-RU") {
  if (!value) {
    return "—";
  }
  return new Intl.DateTimeFormat(locale, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}

export function formatDateTime(value, locale = "ru-RU") {
  if (!value) {
    return "—";
  }
  return `${formatDate(value, locale)} ${formatTime(value, locale)}`;
}

export function buildAbsoluteMediaUrl(baseUrl, mediaPath) {
  if (!mediaPath) {
    return "";
  }
  if (mediaPath.startsWith("http://") || mediaPath.startsWith("https://")) {
    return mediaPath;
  }
  return `${baseUrl.replace(/\/$/, "")}${mediaPath.startsWith("/") ? mediaPath : `/${mediaPath}`}`;
}

export function isMediaFile(value = "") {
  return /\.(png|jpe?g|gif|webp|svg|mp4|webm|mov)$/i.test(value);
}

export function normalizeApiError(error, fallbackMessage) {
  return (
    error?.response?.data?.detail?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    fallbackMessage
  );
}

export function createSequentialIndex(offset, rowIndex) {
  return offset + rowIndex + 1;
}
