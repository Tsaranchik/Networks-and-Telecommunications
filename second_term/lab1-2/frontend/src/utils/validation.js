export async function validateSchema(schema, values) {
  try {
    await schema.validate(values, {
      abortEarly: false,
    });
    return {};
  } catch (error) {
    const fieldErrors = {};
    for (const issue of error.inner || []) {
      if (issue.path && !fieldErrors[issue.path]) {
        fieldErrors[issue.path] = issue.message;
      }
    }
    return fieldErrors;
  }
}
