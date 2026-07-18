#!/usr/bin/env ruby
# frozen_string_literal: true

require 'fileutils'
require 'erb'
require 'gollum-lib'

ROOT = File.expand_path('..', __dir__)
OUTPUT = File.join(ROOT, '_site')
BASE_PATH = ENV.fetch('BASE_PATH', '/wiki').chomp('/')
LAYOUT = File.join(ROOT, '_Layout.html')

SKIP_PAGES = %w[README].freeze

def page_slug(page)
  File.basename(page.url_path, File.extname(page.url_path))
end

def static_href(slug)
  if slug == 'Home'
    "#{BASE_PATH}/"
  else
    "#{BASE_PATH}/#{slug}.html"
  end
end

def output_path(page)
  slug = page_slug(page)
  if slug == 'Home'
    File.join(OUTPUT, 'index.html')
  else
    File.join(OUTPUT, "#{slug}.html")
  end
end

def rewrite_links(html)
  prefix = BASE_PATH.empty? ? '' : BASE_PATH

  html = html.gsub(%r{href="(#{Regexp.escape(prefix)})?/([^"#?]+)(#[^"]*)?"}m) do
    path = Regexp.last_match(2)
    fragment = Regexp.last_match(3) || ''
    slug = File.basename(path, File.extname(path))
    %(href="#{static_href(slug)}#{fragment}")
  end

  html.gsub(%r{src="(#{Regexp.escape(prefix)})?/([^"]+)"}m) do
    path = Regexp.last_match(2)
  %(src="#{prefix}/#{path}")
  end
end

def render_page(page, sidebar_html)
  content = page.formatted_data
  content = rewrite_links(content)

  sidebar = sidebar_html ? rewrite_links(sidebar_html) : nil

  template = ERB.new(File.read(LAYOUT))
  template.result(binding)
end

def copy_assets
  %w[assets custom.css].each do |asset|
    src = File.join(ROOT, asset)
    next unless File.exist?(src)

    dest = File.join(OUTPUT, asset)
    if File.directory?(src)
      FileUtils.cp_r(src, OUTPUT)
    else
      FileUtils.mkdir_p(File.dirname(dest))
      FileUtils.cp(src, dest)
    end
  end
end

wiki = Gollum::Wiki.new(ROOT, base_path: "#{BASE_PATH}/", css: true, display_metadata: false)
sidebar_page = wiki.page('_Sidebar')
sidebar_html = sidebar_page&.formatted_data

FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)

pages = wiki.pages.reject(&:sub_page).reject { |p| SKIP_PAGES.include?(page_slug(p)) }

pages.each do |page|
  dest = output_path(page)
  FileUtils.mkdir_p(File.dirname(dest))
  File.write(dest, render_page(page, sidebar_html))
  puts "  #{page.url_path} -> #{dest.sub(ROOT + '/', '')}"
end

copy_assets
puts "\nBuilt #{pages.size} pages to #{OUTPUT}"
