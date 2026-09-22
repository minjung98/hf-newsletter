"""
Hugging Face Papers Crawler
Hugging Face Daily Papers 페이지에서 논문 정보를 가져옵니다.
"""

import re
import json
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Paper:
    """논문 정보"""
    paper_id: str
    title: str
    summary: str
    authors: List[str]
    organization: Optional[str]
    upvotes: int
    num_comments: int
    published_at: str
    url: str
    thumbnail: Optional[str]
    
    def to_dict(self) -> Dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "summary": self.summary,
            "authors": self.authors,
            "organization": self.organization,
            "upvotes": self.upvotes,
            "num_comments": self.num_comments,
            "published_at": self.published_at,
            "url": f"https://huggingface.co/papers/{self.paper_id}",
            "thumbnail": self.thumbnail
        }


class HuggingFacePapersCrawler:
    """Hugging Face Daily Papers 크롤러"""
    
    BASE_URL = "https://huggingface.co"
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
    
    def fetch_daily_papers(self, date: Optional[str] = None) -> List[Paper]:
        """
        일별 논문 목록 가져오기
        
        Args:
            date: 날짜 형식 (YYYY-MM-DD). None이면 오늘
            
        Returns:
            Paper 객체 리스트
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.BASE_URL}/papers/date/{date}"
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            # HTML에서 JSON 데이터 추출
            papers = self._parse_html_for_papers(response.text)
            return papers
            
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return []
    
    def _parse_html_for_papers(self, html: str) -> List[Paper]:
        """HTML에서 논문 데이터 파싱"""
        papers = []
        
        # 방법 1: dailyPapers 배열 찾기
        json_match = re.search(r'"dailyPapers":\s*(\[.*?\])\s*,\s*"prevDate"', html, re.DOTALL)
        
        # 방법 2: dailyDate 데이터 찾기
        if not json_match:
            json_match = re.search(r'window\.__NEXT_DATA__\s*=\s*(\{.*?\});', html, re.DOTALL)
        
        # 방법 3: Embedded JSON 데이터 찾기
        if not json_match:
            # script 태그 내의 데이터 찾기
            script_matches = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
            for script_content in script_matches:
                try:
                    data = json.loads(script_content)
                    # JSON 구조 탐색
                    if 'props' in data:
                        props = data['props']
                        if 'pageProps' in props:
                            page_props = props['pageProps']
                            if 'dailyPapers' in page_props:
                                daily_papers = page_props['dailyPapers']
                                return self._parse_daily_papers_data(daily_papers)
                except json.JSONDecodeError:
                    continue
        
        if json_match:
            try:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # dailyPapers가 배열인지 확인
                if isinstance(data, list):
                    return self._parse_daily_papers_data(data)
                    
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
        
        # 방법 4: HTML에서 직접 데이터 추출 (fallback)
        return self._parse_html_directly(html)
    
    def _parse_daily_papers_data(self, data: list) -> List[Paper]:
        """dailyPapers 데이터 파싱"""
        papers = []
        
        for item in data:
            paper_data = item.get("paper", {})
            
            # 저자 정보 추출
            authors = []
            for author in paper_data.get("authors", []):
                if isinstance(author, dict):
                    name = author.get("name", "")
                    if name:
                        authors.append(name)
                elif isinstance(author, str):
                    authors.append(author)
            
            # 조직 정보
            org = paper_data.get("organization")
            if org and isinstance(org, dict):
                org_name = org.get("fullname") or org.get("name")
            else:
                org_name = str(org) if org else None
            
            paper = Paper(
                paper_id=paper_data.get("id", ""),
                title=paper_data.get("title", ""),
                summary=paper_data.get("summary", ""),
                authors=authors,
                organization=org_name,
                upvotes=item.get("upvotes", 0),
                num_comments=paper_data.get("numComments", 0),
                published_at=paper_data.get("publishedAt", ""),
                url=f"https://huggingface.co/papers/{paper_data.get('id', '')}",
                thumbnail=paper_data.get("thumbnail")
            )
            papers.append(paper)
        
        return papers
    
    def _parse_html_directly(self, html: str) -> List[Paper]:
        """HTML에서 직접 논문 정보 추출 (fallback)"""
        papers = []
        
        # paper_id 추출
        paper_id_pattern = r'/papers/(\d{4}\.\d{5})'
        paper_ids = re.findall(paper_id_pattern, html)
        
        # 제목 추출
        title_pattern = r'<h3[^>]*class="[^"]*text-lg[^"]*"[^>]*>.*?<a[^>]*class="[^"]*cursor-pointer[^"]*"[^>]*>([^<]+)</a>'
        titles = re.findall(title_pattern, html, re.DOTALL)
        
        # 요약 추출
        summary_pattern = r'"summary":"([^"]+)"'
        summaries = re.findall(summary_pattern, html)
        
        # 저자 추출
        author_pattern = r'"name":"([^"]+)"'
        authors_list = re.findall(author_pattern, html)
        
        # 최소한의 데이터로 논문 생성
        for i, paper_id in enumerate(set(paper_ids)):  # 중복 제거
            title = titles[i] if i < len(titles) else f"Paper {paper_id}"
            summary = summaries[i] if i < len(summaries) else ""
            
            # 이스케이프 문자 처리
            summary = summary.replace('\\n', ' ').replace('\\"', '"').replace('\\u2019', "'")
            
            paper = Paper(
                paper_id=paper_id,
                title=title.strip(),
                summary=summary.strip(),
                authors=["Authors not available"],
                organization=None,
                upvotes=0,
                num_comments=0,
                published_at="",
                url=f"https://huggingface.co/papers/{paper_id}",
                thumbnail=None
            )
            papers.append(paper)
        
        return papers
    
    def fetch_paper_details(self, paper_id: str) -> Optional[Dict]:
        """특정 논문의 상세 정보 가져오기"""
        url = f"{self.BASE_URL}/papers/{paper_id}"
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            # 상세 페이지에서 추가 정보 추출
            # (실제로는 더 많은 정보를 가져올 수 있음)
            return {"url": url, "fetched": True}
            
        except httpx.HTTPError:
            return None
    
    def get_trending_papers(self, limit: int = 10) -> List[Paper]:
        """트렌딩 논문 가져오기"""
        url = f"{self.BASE_URL}/papers/trending"
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            papers = self._parse_html_for_papers(response.text)
            return papers[:limit]
            
        except httpx.HTTPError:
            return []
    
    def close(self):
        """클라이언트 종료"""
        self.client.close()


# 테스트 코드
if __name__ == "__main__":
    crawler = HuggingFacePapersCrawler()
    
    print("📚 오늘의 Hugging Face Daily Papers 가져오는 중...")
    papers = crawler.fetch_daily_papers()
    
    print(f"\n✅ {len(papers)}개의 논문을 찾았습니다!\n")
    
    for i, paper in enumerate(papers[:5], 1):
        print(f"{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"   Upvotes: {paper.upvotes}")
        print(f"   URL: {paper.url}")
        print()
    
    crawler.close()
