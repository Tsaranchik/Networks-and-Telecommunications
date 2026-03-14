import { formatDate, formatDateTime, formatNumber, formatTime } from "./formatters";

export function installFormatting(app) {
  const filters = {
    date: formatDate,
    time: formatTime,
    dateTime: formatDateTime,
    number: formatNumber,
  };

  app.config.globalProperties.$filters = filters;
  app.mixin({
    methods: {
      $formatDateValue(value, locale = "ru-RU") {
        return filters.date(value, locale);
      },
      $formatTimeValue(value, locale = "ru-RU") {
        return filters.time(value, locale);
      },
      $formatNumberValue(value, locale = "ru") {
        return filters.number(value, locale);
      },
    },
  });
}
