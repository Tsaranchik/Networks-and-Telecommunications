import * as yup from "yup";

const requiredText = (t) => yup.string().trim().required(t("validation.required"));
const positiveNumber = (t) =>
  yup
    .number()
    .typeError(t("validation.required"))
    .positive(t("validation.positive"))
    .required(t("validation.required"));
const requiredSelect = (t) =>
  yup
    .number()
    .typeError(t("validation.chooseValue"))
    .required(t("validation.chooseValue"));

export const entityConfigs = {
  "scholarship-types": {
    key: "scholarship-types",
    endpoint: "/scholarship-types",
    columns: [
      { key: "name", labelKey: "fields.name", type: "text", sortable: true },
      { key: "base_amount", labelKey: "fields.base_amount", type: "number", sortable: true },
    ],
    filterFields: [
      { key: "name", labelKey: "fields.name", type: "text" },
      { key: "base_amount", labelKey: "fields.base_amount", type: "number", step: "0.01" },
    ],
    formFields: [
      { key: "name", labelKey: "fields.name", type: "text", required: true },
      { key: "base_amount", labelKey: "fields.base_amount", type: "number", required: true, step: "0.01" },
    ],
    schema: (t) =>
      yup.object({
        name: requiredText(t),
        base_amount: positiveNumber(t),
      }),
  },
  universities: {
    key: "universities",
    endpoint: "/universities",
    columns: [{ key: "name", labelKey: "fields.name", type: "text", sortable: true }],
    filterFields: [{ key: "name", labelKey: "fields.name", type: "text" }],
    formFields: [{ key: "name", labelKey: "fields.name", type: "text", required: true }],
    schema: (t) =>
      yup.object({
        name: requiredText(t),
      }),
  },
  "university-coeffs": {
    key: "university-coeffs",
    endpoint: "/university-coeffs",
    columns: [
      {
        key: "university_id",
        displayKey: "university_name",
        labelKey: "fields.university_name",
        type: "select",
        sortable: true,
      },
      {
        key: "scholarship_type_id",
        displayKey: "scholarship_type_name",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        sortable: true,
      },
      { key: "coeff", labelKey: "fields.coeff", type: "number", sortable: true },
    ],
    filterFields: [
      {
        key: "university_id",
        labelKey: "fields.university_name",
        type: "select",
        lookup: {
          endpoint: "/universities",
          labelKey: "name",
          valueKey: "id",
        },
      },
      {
        key: "scholarship_type_id",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        lookup: {
          endpoint: "/scholarship-types",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "coeff", labelKey: "fields.coeff", type: "number", step: "0.0001" },
    ],
    formFields: [
      {
        key: "university_id",
        labelKey: "fields.university_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/universities",
          labelKey: "name",
          valueKey: "id",
        },
      },
      {
        key: "scholarship_type_id",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/scholarship-types",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "coeff", labelKey: "fields.coeff", type: "number", required: true, step: "0.0001" },
    ],
    schema: (t) =>
      yup.object({
        university_id: requiredSelect(t),
        scholarship_type_id: requiredSelect(t),
        coeff: positiveNumber(t),
      }),
  },
  groups: {
    key: "groups",
    endpoint: "/groups",
    columns: [
      { key: "name", labelKey: "fields.name", type: "text", sortable: true },
      { key: "course", labelKey: "fields.course", type: "number", sortable: true },
      { key: "admission_year", labelKey: "fields.admission_year", type: "number", sortable: true },
      {
        key: "university_id",
        displayKey: "university_name",
        labelKey: "fields.university_name",
        type: "select",
        sortable: true,
      },
      { key: "curator_full_name", labelKey: "fields.curator_full_name", type: "text", sortable: true },
    ],
    filterFields: [
      { key: "name", labelKey: "fields.name", type: "text" },
      { key: "course", labelKey: "fields.course", type: "number", step: "1" },
      { key: "admission_year", labelKey: "fields.admission_year", type: "number", step: "1" },
      {
        key: "university_id",
        labelKey: "fields.university_name",
        type: "select",
        lookup: {
          endpoint: "/universities",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "curator_full_name", labelKey: "fields.curator_full_name", type: "text" },
    ],
    formFields: [
      { key: "name", labelKey: "fields.name", type: "text", required: true },
      { key: "course", labelKey: "fields.course", type: "number", required: true, step: "1" },
      { key: "admission_year", labelKey: "fields.admission_year", type: "number", required: true, step: "1" },
      {
        key: "university_id",
        labelKey: "fields.university_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/universities",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "curator_full_name", labelKey: "fields.curator_full_name", type: "text", required: true },
      { key: "curator_photo", labelKey: "fields.curator_photo", type: "upload", accept: "image/*,video/*" },
    ],
    schema: (t) =>
      yup.object({
        name: requiredText(t),
        course: yup.number().typeError(t("validation.required")).min(1).max(6).required(t("validation.required")),
        admission_year: yup
          .number()
          .typeError(t("validation.required"))
          .min(1990)
          .max(2100)
          .required(t("validation.required")),
        university_id: requiredSelect(t),
        curator_full_name: requiredText(t),
        curator_photo: yup.string().nullable(),
      }),
  },
  students: {
    key: "students",
    endpoint: "/students",
    columns: [
      { key: "full_name", labelKey: "fields.full_name", type: "text", sortable: true },
      { key: "group_id", displayKey: "group_name", labelKey: "fields.group_name", type: "select", sortable: true },
      { key: "address", labelKey: "fields.address", type: "text", sortable: false },
    ],
    filterFields: [
      { key: "full_name", labelKey: "fields.full_name", type: "text" },
      {
        key: "group_id",
        labelKey: "fields.group_name",
        type: "select",
        lookup: {
          endpoint: "/groups",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "address", labelKey: "fields.address", type: "text" },
    ],
    formFields: [
      { key: "full_name", labelKey: "fields.full_name", type: "text", required: true },
      {
        key: "group_id",
        labelKey: "fields.group_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/groups",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "address", labelKey: "fields.address", type: "textarea", required: true },
    ],
    schema: (t) =>
      yup.object({
        full_name: requiredText(t),
        group_id: requiredSelect(t),
        address: requiredText(t),
      }),
  },
  "scholarship-assignments": {
    key: "scholarship-assignments",
    endpoint: "/scholarship-assignments",
    columns: [
      {
        key: "student_id",
        displayKey: "student_full_name",
        labelKey: "fields.student_full_name",
        type: "select",
        sortable: true,
      },
      { key: "semester", labelKey: "fields.semester", type: "number", sortable: true },
      {
        key: "scholarship_type_id",
        displayKey: "scholarship_type_name",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        sortable: true,
      },
      { key: "amount", labelKey: "fields.amount", type: "number", sortable: true },
    ],
    filterFields: [
      {
        key: "student_id",
        labelKey: "fields.student_full_name",
        type: "select",
        lookup: {
          endpoint: "/students",
          labelKey: "full_name",
          valueKey: "id",
        },
      },
      { key: "semester", labelKey: "fields.semester", type: "number", step: "1" },
      {
        key: "scholarship_type_id",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        lookup: {
          endpoint: "/scholarship-types",
          labelKey: "name",
          valueKey: "id",
        },
      },
      { key: "amount", labelKey: "fields.amount", type: "number", step: "0.01" },
    ],
    formFields: [
      {
        key: "student_id",
        labelKey: "fields.student_full_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/students",
          labelKey: "full_name",
          valueKey: "id",
        },
      },
      { key: "semester", labelKey: "fields.semester", type: "number", required: true, step: "1" },
      {
        key: "scholarship_type_id",
        labelKey: "fields.scholarship_type_name",
        type: "select",
        required: true,
        lookup: {
          endpoint: "/scholarship-types",
          labelKey: "name",
          valueKey: "id",
        },
      },
    ],
    schema: (t) =>
      yup.object({
        student_id: requiredSelect(t),
        semester: yup.number().typeError(t("validation.required")).min(1).max(20).required(t("validation.required")),
        scholarship_type_id: requiredSelect(t),
      }),
  },
};

export const entityOrder = Object.keys(entityConfigs);
