#!/usr/bin/env ruby
# frozen_string_literal: true

require 'fileutils'
require 'erb'
require 'json'
require 'yaml'
require 'nokogiri'
require 'gollum-lib'
require 'cgi'

ROOT = File.expand_path('..', __dir__)
OUTPUT = File.join(ROOT, '_site')
BASE_PATH = ENV.fetch('BASE_PATH', '').chomp('/')
SITE_URL = ENV.fetch('SITE_URL', 'https://wiki.giljae.com')
CUSTOM_DOMAIN = ENV.fetch('CUSTOM_DOMAIN', 'wiki.giljae.com')
GITHUB_REPO = ENV.fetch('GITHUB_REPO', 'giljae/wiki')
GITHUB_BRANCH = ENV.fetch('GITHUB_BRANCH', 'main')
LAYOUT = File.join(ROOT, '_Layout.html')
SITE_NAME = "Giljae's Digital Garden"
SITE_DESCRIPTION = "#{SITE_NAME} — Gollum 기반 개인 위키"

SKIP_PAGES = %w[README 404].freeze
ASSET_PREFIXES = %w[assets].freeze

def page_slug(page)
  page.url_path.sub(/\.(md|markdown)$/i, '')
end

def normalize_path(path)
  path.to_s.sub(%r{\A/}, '').sub(/\.(md|markdown)$/i, '')
end

def static_href(path)
  normalized = normalize_path(path)
  return '/' if normalized.empty? || normalized == 'Home'

  base = BASE_PATH.empty? ? '' : BASE_PATH
  "#{base}/#{normalized}/"
end

def canonical_url(path)
  "#{SITE_URL.chomp('/')}#{static_href(path)}"
end

def output_path(page)
  slug = page_slug(page)
  if slug == 'Home'
    File.join(OUTPUT, 'index.html')
  else
    File.join(OUTPUT, slug, 'index.html')
  end
end

def github_file_path(page)
  page.path
end

def github_edit_url(page)
  "https://github.com/#{GITHUB_REPO}/edit/#{GITHUB_BRANCH}/#{github_file_path(page)}"
end

def github_history_url(page)
  "https://github.com/#{GITHUB_REPO}/commits/#{GITHUB_BRANCH}/#{github_file_path(page)}"
end

def page_link?(path)
  return false if path.start_with?('#')
  return false if ASSET_PREFIXES.any? { |p| path.start_with?("#{p}/") }

  ext = File.extname(path)
  ext.empty? || ext.match?(/\.(md|markdown)$/i)
end

def rewrite_links(html)
  prefix = BASE_PATH.empty? ? '' : BASE_PATH

  html = html.gsub(%r{href="(#{Regexp.escape(prefix)})?/([^"#?]+)(#[^"]*)?"}m) do
    full = $&
    path = Regexp.last_match(2)
    fragment = Regexp.last_match(3) || ''
    next full if path.end_with?('/')
    next full unless page_link?(path)

    %(href="#{static_href(path)}#{fragment}")
  end

  html.gsub(%r{src="(#{Regexp.escape(prefix)})?/([^"]+)"}m) do
    path = Regexp.last_match(2)
    %(src="#{prefix}/#{path}")
  end
end

def plain_text(html)
  Nokogiri::HTML(html).text.gsub(/\s+/, ' ').strip
end

def page_description(page, html)
  text = plain_text(html)
  text.length > 160 ? "#{text[0, 157]}..." : text
end

def extract_toc_and_content(html)
  doc = Nokogiri::HTML.fragment(html)
  toc = doc.at_css('.toc')
  toc_html = toc ? toc.to_html : nil
  toc&.remove
  [doc.to_html, toc_html]
end

def folder_index_slug(path_so_far, pages_by_slug)
  index_slug = "#{path_so_far}/Home"
  pages_by_slug[index_slug] ? index_slug : nil
end

def breadcrumb_url(path_so_far, pages_by_slug)
  return static_href(path_so_far) if path_so_far == 'tags' || path_so_far.start_with?('tags/')
  return static_href(path_so_far) if pages_by_slug[path_so_far]

  index = folder_index_slug(path_so_far, pages_by_slug)
  return static_href(index) if index

  nil
end

def page_raw_data(page)
  path = File.join(ROOT, page.path)
  File.exist?(path) ? File.read(path) : page.raw_data
end

def parse_front_matter(raw)
  return [{}, raw] unless raw.match?(/\A---\s*\n/)

  if raw =~ /\A---\s*\n(.*?)\n---\s*\n(.*)\z/m
    meta = YAML.safe_load(Regexp.last_match(1), permitted_classes: [Date, Time], aliases: true) || {}
    [meta, Regexp.last_match(2)]
  else
    [{}, raw]
  end
end

def page_metadata(page)
  parse_front_matter(page_raw_data(page)).first
end

def page_body(page)
  parse_front_matter(page_raw_data(page)).last
end

def page_tags(page)
  Array(page_metadata(page)['tags']).map(&:to_s).map(&:strip).reject(&:empty?)
end

def tag_slug(tag)
  tag.to_s.strip.downcase.gsub(/\s+/, '-')
end

def tag_href(tag)
  base = BASE_PATH.empty? ? '' : BASE_PATH
  "#{base}/tags/#{tag_slug(tag)}/"
end

def tags_index_href
  base = BASE_PATH.empty? ? '' : BASE_PATH
  "#{base}/tags/"
end

def page_formatted_data(page)
  body = page_body(page)
  if body != page.raw_data
    page.define_singleton_method(:text_data) { body }
    page.remove_instance_variable(:@formatted_data) if page.instance_variable_defined?(:@formatted_data)
  end
  page.formatted_data
end

def build_tag_index(pages)
  index = Hash.new { |h, k| h[k] = { display: nil, pages: [] } }

  pages.each do |page|
    slug = page_slug(page)
    page_tags(page).each do |tag|
      key = tag_slug(tag)
      index[key][:display] ||= tag
      index[key][:pages] << {
        slug: slug,
        title: page.title,
        date: page.version&.authored_date
      }
    end
  end

  index.each_value do |entry|
    entry[:pages] = entry[:pages].uniq { |p| p[:slug] }
                              .sort_by { |p| [-(p[:date]&.to_i || 0), p[:title].downcase] }
  end

  index
end

def render_tag_pills_html(tags)
  return nil if tags.empty?

  pills = tags.sort_by(&:downcase).map do |tag|
    %(<a class="tag-pill" href="#{tag_href(tag)}">#{CGI.escapeHTML(tag)}</a>)
  end

  %(<div class="page-tags">#{pills.join}</div>)
end

def render_tag_cloud_html(tag_index, limit: 14)
  return '' if tag_index.empty?

  sorted = tag_index.sort_by { |_, entry| [-entry[:pages].length, entry[:display].downcase] }
  items = sorted.first(limit).map do |key, entry|
    %(<a class="tag-pill tag-pill-sm" href="#{tag_href(entry[:display])}">#{CGI.escapeHTML(entry[:display])}<span class="tag-count">#{entry[:pages].length}</span></a>)
  end

  more = if tag_index.length > limit
           %(<a class="tag-more" href="#{tags_index_href}">+#{tag_index.length - limit}</a>)
         else
           ''
         end

  %(<div class="nav-section nav-tags"><p class="nav-heading">태그</p><div class="tag-cloud">#{items.join}#{more}</div><a class="nav-tags-all" href="#{tags_index_href}">모든 태그</a></div>)
end

def render_dashboard_html(pages, tag_index)
  recent = pages.sort_by { |p| -(p.version&.authored_date&.to_i || 0) }.first(6)
  recent_items = recent.map do |page|
    slug = page_slug(page)
    date = page.version&.authored_date&.strftime('%Y-%m-%d') || ''
    tags = page_tags(page)
    tag_html = tags.first ? %(<span class="dashboard-tag">#{CGI.escapeHTML(tags.first)}</span>) : ''
    %(<li><a href="#{static_href(slug)}">#{CGI.escapeHTML(page.title)}</a>#{tag_html}<time>#{date}</time></li>)
  end

  tag_items = tag_index.sort_by { |_, e| [-e[:pages].length, e[:display].downcase] }.first(12).map do |_, entry|
    %(<a class="tag-pill" href="#{tag_href(entry[:display])}">#{CGI.escapeHTML(entry[:display])}<span class="tag-count">#{entry[:pages].length}</span></a>)
  end

  quick_links = [
    { title: '시작 가이드', slug: 'Getting-Started', desc: '편집 방법과 문법' },
    { title: '플러그인', slug: 'Plugins', desc: 'Mermaid, KaTeX, 검색' },
    { title: 'notes', slug: 'notes/Home', desc: '폴더 예시' },
    { title: '모든 태그', slug: nil, href: tags_index_href, desc: '태그별 문서 목록' }
  ]
  quick_html = quick_links.map do |link|
    href = link[:href] || static_href(link[:slug])
    %(<a class="dashboard-link" href="#{href}"><strong>#{CGI.escapeHTML(link[:title])}</strong><span>#{CGI.escapeHTML(link[:desc])}</span></a>)
  end

  tagged_count = pages.count { |p| !page_tags(p).empty? }

  <<~HTML
    <section class="wiki-dashboard" aria-label="위키 대시보드">
      <div class="dashboard-grid">
        <div class="dashboard-card dashboard-recent">
          <h2>최근 편집</h2>
          <ul>#{recent_items.join}</ul>
        </div>
        <div class="dashboard-card dashboard-tags">
          <h2>태그 <a class="dashboard-more" href="#{tags_index_href}">전체</a></h2>
          <div class="tag-cloud">#{tag_items.join}</div>
        </div>
        <div class="dashboard-card dashboard-links">
          <h2>바로가기</h2>
          <div class="dashboard-link-grid">#{quick_html.join}</div>
        </div>
        <div class="dashboard-card dashboard-stats">
          <h2>통계</h2>
          <dl>
            <div><dt>문서</dt><dd>#{pages.length}</dd></div>
            <div><dt>태그</dt><dd>#{tag_index.length}</dd></div>
            <div><dt>태그된 문서</dt><dd>#{tagged_count}</dd></div>
          </dl>
        </div>
      </div>
    </section>
  HTML
end

def render_tags_index_content(tag_index)
  if tag_index.empty?
    return '<p class="dashboard-empty">아직 태그가 없습니다. 페이지 상단에 YAML front matter로 <code>tags</code>를 추가해 보세요.</p>'
  end

  items = tag_index.sort_by { |_, entry| entry[:display].downcase }.map do |_, entry|
    preview = entry[:pages].first(3).map do |page|
      %(<a href="#{static_href(page[:slug])}">#{CGI.escapeHTML(page[:title])}</a>)
    end
    more = entry[:pages].length > 3 ? %( · <span class="tag-more-pages">외 #{entry[:pages].length - 3}개</span>) : ''
    %(<li class="tag-index-item"><a class="tag-pill tag-pill-lg" href="#{tag_href(entry[:display])}">#{CGI.escapeHTML(entry[:display])}<span class="tag-count">#{entry[:pages].length}</span></a><p class="tag-index-preview">#{preview.join(', ')}#{more}</p></li>)
  end

  <<~HTML
    <p>태그를 클릭하면 해당 태그가 붙은 문서를 모아 볼 수 있습니다.</p>
    <ul class="tag-index-list">#{items.join}</ul>
  HTML
end

def render_single_tag_content(tag_entry)
  items = tag_entry[:pages].map do |page|
    date = page[:date]&.strftime('%Y-%m-%d') || ''
    %(<li><a href="#{static_href(page[:slug])}">#{CGI.escapeHTML(page[:title])}</a><time>#{date}</time></li>)
  end

  <<~HTML
    <p><strong>#{CGI.escapeHTML(tag_entry[:display])}</strong> 태그가 붙은 문서 #{tag_entry[:pages].length}개</p>
    <ul class="tag-page-list">#{items.join}</ul>
    <p><a href="#{tags_index_href}">← 모든 태그</a></p>
  HTML
end

def virtual_page(title:, path:)
  Struct.new(:title, :path, :version, keyword_init: true).new(title: title, path: path, version: nil)
end

def build_breadcrumbs_for_slug(slug, pages_by_slug, title: nil)
  if slug == 'Home'
    return [{ label: 'Home', url: nil }]
  end

  crumbs = [{ label: 'Home', url: static_href('Home') }]

  parts = slug.split('/')
  parts.each_with_index do |_part, i|
    path_so_far = parts[0..i].join('/')
    page = pages_by_slug[path_so_far]
    index_slug = folder_index_slug(path_so_far, pages_by_slug)
    index_page = index_slug && pages_by_slug[index_slug]

    label = if page
              page.title
            elsif path_so_far == 'tags'
              '태그'
            elsif title && i == parts.length - 1
              title
            elsif index_page && i == parts.length - 1
              index_page.title
            elsif index_page
              File.basename(path_so_far)
            else
              parts[i]
            end

    url = if i == parts.length - 1
            nil
          else
            breadcrumb_url(path_so_far, pages_by_slug)
          end

    crumbs << { label: label, url: url }
  end
  crumbs
end

def build_breadcrumbs(slug, pages_by_slug)
  build_breadcrumbs_for_slug(slug, pages_by_slug)
end

def build_nav_tree(pages)
  root = {}
  pages.each do |page|
    slug = page_slug(page)
    parts = slug.split('/')
    node = root
    parts.each_with_index do |part, idx|
      node[part] ||= { 'children' => {}, 'page' => nil }
      node[part]['page'] = page if idx == parts.length - 1
      node = node[part]['children']
    end
  end
  root
end

def build_backlink_index(pages)
  index = Hash.new { |h, k| h[k] = [] }

  pages.each do |source|
    source_slug = page_slug(source)
    page_body(source).scan(/\[\[([^\]|#]+)(?:#[^\]]+)?(?:\|[^\]]+)?\]\]/) do |match|
      target = normalize_path(match[0].strip)
      next if target.empty? || target == source_slug

      index[target] << { slug: source_slug, title: source.title }
    end
  end

  index.transform_values { |arr| arr.uniq { |item| item[:slug] } }
end

def render_backlinks_html(slug, backlink_index)
  links = backlink_index[slug]
  return nil if links.nil? || links.empty?

  items = links.sort_by { |l| l[:title].downcase }.map do |link|
    %(<li><a href="#{static_href(link[:slug])}">#{CGI.escapeHTML(link[:title])}</a></li>)
  end

  <<~HTML
    <section class="wiki-backlinks">
      <h2>이 문서를 링크한 페이지</h2>
      <ul>#{items.join}</ul>
    </section>
  HTML
end

def build_recent_html(pages, limit: 8)
  sorted = pages.sort_by { |p| -(p.version&.authored_date&.to_i || 0) }
  items = sorted.first(limit).map do |page|
    slug = page_slug(page)
    date = page.version&.authored_date&.strftime('%Y-%m-%d') || ''
    %(<li><a href="#{static_href(slug)}">#{CGI.escapeHTML(page.title)}</a><time class="nav-date">#{date}</time></li>)
  end

  <<~HTML
    <div class="nav-section nav-recent">
      <p class="nav-heading">최근 편집</p>
      <ul class="nav-recent-list">#{items.join}</ul>
    </div>
  HTML
end
def nav_page_title(node, key)
  node['page'] ? node['page'].title : key
end

def render_nav_tree(nodes, parent_slug = '')
  return '' if nodes.empty?

  items = nodes.sort_by { |key, _| key == 'Home' ? '' : key.downcase }.map do |key, node|
    full_slug = parent_slug.empty? ? key : "#{parent_slug}/#{key}"
    title = CGI.escapeHTML(nav_page_title(node, key))
    has_children = !node['children'].empty?

    if node['page']
      link = %(<a href="#{static_href(full_slug)}" data-slug="#{full_slug}">#{title}</a>)
    elsif (index_slug = folder_index_slug(full_slug, @pages_by_slug))
      link = %(<a href="#{static_href(index_slug)}" data-slug="#{full_slug}" class="nav-folder-link">#{title}</a>)
    else
      link = %(<span class="nav-folder-label" data-slug="#{full_slug}">#{title}</span>)
    end

    child_html = has_children ? render_nav_tree(node['children'], full_slug) : ''
    toggle = if has_children
               %(<button type="button" class="nav-toggle" aria-expanded="true" aria-label="하위 문서 접기/펼치기"></button>)
             else
               ''
             end
    %(<li class="nav-item#{has_children ? ' nav-has-children nav-open' : ''}" data-slug="#{full_slug}">#{toggle}#{link}#{child_html}</li>)
  end

  %(<ul class="nav-tree">#{items.join}</ul>)
end

def build_sidebar_html(_wiki, pages, tag_index)
  @pages_by_slug = pages.to_h { |p| [page_slug(p), p] }
  tree = build_nav_tree(pages)
  tree_html = render_nav_tree(tree)
  recent_html = build_recent_html(pages)
  tags_html = render_tag_cloud_html(tag_index)
  %(<div class="nav-section"><p class="nav-heading">문서 목록</p>#{tree_html}</div>#{tags_html}#{recent_html})
ensure
  @pages_by_slug = nil
end

def render_page(page, sidebar_html, footer_html, pages_by_slug, backlink_index, options = {})
  opts = {
    tag_index: {},
    all_pages: [],
    slug: nil,
    content_override: nil,
    tags: nil,
    dashboard: false,
    edit_url: nil,
    history_url: nil,
    breadcrumb_title: nil,
    virtual_page: false
  }.merge(options)

  slug = opts[:slug] || page_slug(page)

  if opts[:content_override]
    content = rewrite_links(opts[:content_override])
    toc_html = nil
  else
    raw_html = page_formatted_data(page)
    content, toc_html = extract_toc_and_content(raw_html)
    content = rewrite_links(content)
    content = render_dashboard_html(opts[:all_pages], opts[:tag_index]) + content if opts[:dashboard]
  end

  tags = opts[:tags] || (opts[:virtual_page] ? [] : page_tags(page))
  tags_html = render_tag_pills_html(tags)

  sidebar = sidebar_html
  footer = footer_html ? rewrite_links(footer_html) : nil

  display_title = if opts[:virtual_page]
                    page.title
                  else
                    page_metadata(page)['title'] || page.title
                  end

  site_description = SITE_DESCRIPTION
  site_name = SITE_NAME
  document_title = slug == 'Home' ? site_name : "#{display_title} — #{site_name}"
  meta_description = if opts[:virtual_page] && slug == 'tags'
                       '태그별로 분류된 위키 문서 목록'
                     elsif opts[:virtual_page]
                       "#{display_title} 태그가 붙은 위키 문서"
                     elsif opts[:content_override]
                       plain_text(content)[0, 160]
                     else
                       page_description(page, content)
                     end
  canonical = canonical_url(slug)
  breadcrumbs = build_breadcrumbs_for_slug(slug, pages_by_slug, title: opts[:breadcrumb_title])
  edit_url = opts[:edit_url] || github_edit_url(page)
  history_url = opts[:history_url] || github_history_url(page)
  current_slug = slug
  toc_sidebar = toc_html
  backlinks_html = opts[:virtual_page] ? nil : render_backlinks_html(slug, backlink_index)
  virtual_page = opts[:virtual_page]

  template = ERB.new(File.read(LAYOUT))
  template.result(binding)
end

def copy_assets
  assets_dir = File.join(ROOT, 'assets')
  FileUtils.cp_r(assets_dir, OUTPUT) if File.directory?(assets_dir)

  custom = File.join(ROOT, 'custom.css')
  FileUtils.cp(custom, OUTPUT) if File.exist?(custom)
end

def build_search_index(pages)
  pages.map do |page|
    html = page_formatted_data(page)
    slug = page_slug(page)
    tags = page_tags(page)
    {
      'title' => page.title,
      'url' => static_href(slug),
      'content' => ([tags.join(' ')] + [plain_text(html)]).join(' ').strip
    }
  end
end

def build_sitemap(pages, tag_index)
  urls = pages.map do |page|
    slug = page_slug(page)
    <<~XML.strip
      <url>
        <loc>#{canonical_url(slug)}</loc>
        <lastmod>#{page.version&.authored_date&.strftime('%Y-%m-%d') || Time.now.strftime('%Y-%m-%d')}</lastmod>
      </url>
    XML
  end

  urls << <<~XML.strip
    <url>
      <loc>#{canonical_url('tags')}</loc>
      <lastmod>#{Time.now.strftime('%Y-%m-%d')}</lastmod>
    </url>
  XML

  tag_index.each_key do |key|
    urls << <<~XML.strip
      <url>
        <loc>#{canonical_url("tags/#{key}")}</loc>
        <lastmod>#{Time.now.strftime('%Y-%m-%d')}</lastmod>
      </url>
    XML
  end

  <<~XML
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    #{urls.join("\n")}
    </urlset>
  XML
end

def build_robots
  base = BASE_PATH.empty? ? '' : BASE_PATH
  <<~ROBOTS
    User-agent: *
    Allow: /

    Sitemap: #{SITE_URL.chomp('/')}#{base}/sitemap.xml
  ROBOTS
end

FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)

wiki = Gollum::Wiki.new(ROOT, base_path: "#{BASE_PATH}/", css: true, display_metadata: false)
footer_page = wiki.page('_Footer')
footer_html = footer_page&.formatted_data

pages = wiki.pages.reject(&:sub_page).reject { |p| SKIP_PAGES.include?(page_slug(p)) }
pages_by_slug = pages.to_h { |p| [page_slug(p), p] }
tag_index = build_tag_index(pages)
backlink_index = build_backlink_index(pages)
sidebar_html = build_sidebar_html(wiki, pages, tag_index)
render_opts = { tag_index: tag_index, all_pages: pages }
guide_url = "https://github.com/#{GITHUB_REPO}/blob/#{GITHUB_BRANCH}/Getting-Started.md"

pages.each do |page|
  dest = output_path(page)
  FileUtils.mkdir_p(File.dirname(dest))
  page_opts = render_opts.merge(dashboard: page_slug(page) == 'Home')
  File.write(dest, render_page(page, sidebar_html, footer_html, pages_by_slug, backlink_index, page_opts))
  puts "  #{page.url_path} -> #{dest.sub(ROOT + '/', '')}"
end

FileUtils.mkdir_p(File.join(OUTPUT, 'tags'))
tags_index_dest = File.join(OUTPUT, 'tags', 'index.html')
File.write(
  tags_index_dest,
  render_page(
    virtual_page(title: '태그', path: 'tags/index.md'),
    sidebar_html, footer_html, pages_by_slug, backlink_index,
    render_opts.merge(
      slug: 'tags',
      content_override: render_tags_index_content(tag_index),
      breadcrumb_title: '태그',
      virtual_page: true,
      edit_url: guide_url
    )
  )
)
puts '  tags/index -> tags/index.html'

tag_index.each do |key, entry|
  tag_dest = File.join(OUTPUT, 'tags', key, 'index.html')
  FileUtils.mkdir_p(File.dirname(tag_dest))
  File.write(
    tag_dest,
    render_page(
      virtual_page(title: entry[:display], path: "tags/#{key}.md"),
      sidebar_html, footer_html, pages_by_slug, backlink_index,
      render_opts.merge(
        slug: "tags/#{key}",
        content_override: render_single_tag_content(entry),
        breadcrumb_title: entry[:display],
        virtual_page: true,
        edit_url: guide_url
      )
    )
  )
  puts "  tags/#{key} -> tags/#{key}/index.html"
end

error_page = wiki.page('404')
if error_page
  File.write(File.join(OUTPUT, '404.html'), render_page(error_page, sidebar_html, footer_html, pages_by_slug, backlink_index, render_opts))
  puts '  404.md -> 404.html'
end

copy_assets
File.write(File.join(OUTPUT, 'search-index.json'), JSON.pretty_generate(build_search_index(pages)))
File.write(File.join(OUTPUT, 'sitemap.xml'), build_sitemap(pages, tag_index))
File.write(File.join(OUTPUT, 'robots.txt'), build_robots)
File.write(File.join(OUTPUT, 'CNAME'), "#{CUSTOM_DOMAIN}\n") unless CUSTOM_DOMAIN.to_s.strip.empty?
puts '  search-index.json'
puts '  sitemap.xml'
puts '  robots.txt'
puts "  CNAME (#{CUSTOM_DOMAIN})" unless CUSTOM_DOMAIN.to_s.strip.empty?
puts "\nBuilt #{pages.size} pages to #{OUTPUT}"
