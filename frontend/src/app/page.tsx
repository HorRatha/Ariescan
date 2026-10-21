"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Ariescan</h1>
            </div>
            <div className="flex gap-4">
              <Link href="#" className="text-gray-600 hover:text-gray-900">
                Documentation
              </Link>
              <Link href="#" className="text-gray-600 hover:text-gray-900">
                GitHub
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold mb-4">
            Automated API Testing Platform
          </h1>
          <p className="text-xl mb-8 text-blue-100">
            Discover endpoints, generate tests, and validate APIs automatically
          </p>
          <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
            Get Started
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12">Key Features</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Auto Discovery
                </h3>
              </div>
              <p className="text-gray-600">
                Automatically discover API endpoints from OpenAPI documentation
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Test Generation
                </h3>
              </div>
              <p className="text-gray-600">
                Intelligent test case generation without requiring AI
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Comprehensive Testing
                </h3>
              </div>
              <p className="text-gray-600">
                Support for GET, POST, PUT, PATCH, DELETE with full validation
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Security Analysis
                </h3>
              </div>
              <p className="text-gray-600">
                Identify unexpected behavior and common API security issues
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Clear Reports
                </h3>
              </div>
              <p className="text-gray-600">
                Visual test results and detailed analytics dashboards
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-xl font-bold text-blue-600">
                  Local First
                </h3>
              </div>
              <p className="text-gray-600">
                Run everything locally without paying for hosting
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-lg text-gray-600 mb-8">
            Start testing your APIs with Ariescan today
          </p>
          <div className="flex gap-4 justify-center">
            <button className="btn-primary">
              Launch App
            </button>
            <button className="btn-secondary">
              View Documentation
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-bold mb-4">Ariescan</h3>
              <p className="text-gray-400">
                Open-source API testing platform
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="text-gray-400 space-y-2">
                <li><Link href="#" className="hover:text-white">Features</Link></li>
                <li><Link href="#" className="hover:text-white">Documentation</Link></li>
                <li><Link href="#" className="hover:text-white">Roadmap</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Community</h4>
              <ul className="text-gray-400 space-y-2">
                <li><Link href="#" className="hover:text-white">GitHub</Link></li>
                <li><Link href="#" className="hover:text-white">Issues</Link></li>
                <li><Link href="#" className="hover:text-white">Discussions</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="text-gray-400 space-y-2">
                <li><Link href="#" className="hover:text-white">License</Link></li>
                <li><Link href="#" className="hover:text-white">Privacy</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Ariescan. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
