const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
      <h1 className="text-3xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        The page you are looking for does not exist.
      </p>
      <a href="/" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        Go Home
      </a>
    </div>
  );
};

export default NotFoundPage;