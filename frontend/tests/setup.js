import '@testing-library/jest-dom';

if (!URL.createObjectURL) URL.createObjectURL = () => 'blob:local-test-source';
if (!URL.revokeObjectURL) URL.revokeObjectURL = () => {};

afterEach(()=>localStorage.clear());
