"""
Paper Filter Module
특정 분야 논문 필터링
"""

from typing import List, Set
from dataclasses import dataclass

from crawler import Paper


@dataclass
class FilterConfig:
    """필터 설정"""
    # 필터링 키워드 (OR 조건)
    include_keywords: Set[str] = None
    
    # 제외 키워드
    exclude_keywords: Set[str] = None
    
    def __post_init__(self):
        if self.include_keywords is None:
            self.include_keywords = set()
        if self.exclude_keywords is None:
            self.exclude_keywords = set()


class PaperFilter:
    """논문 필터"""
    
    # 미리 정의된 필터 Presets
    PRESETS = {
        "robotics": {
            "name": "로보틱스",
            "include": {
                "robot", "robotics", "manipulation", "grasping", "locomotion",
                "motion planning", "control", "actuator", "autonomous", "drone", "uav",
                "manipulator", "bipedal", "quadruped", "humanoid", "soft robot",
                "micro robot", "diffusion policy", "diffusion model", "action generation",
                "policy learning", "imitation learning", "behavior cloning", "reinforcement learning",
                "visual affordance", "scene understanding", "pose estimation", "in-hand manipulation",
                "reorientation", "rearrangement", "contact model", "grasp planning",
                "model predictive control", "mpc", "trajectory optimization", "whole-body control",
                "slam", "path planning", "obstacle avoidance", "mapping", "localization",
                "bin picking", "pick and place", "assembly", "dexterous manipulation",
                "isaac gym", "mujoco", "physics simulation", "rigid body"
            },
            "exclude": set()
        },
        
        "physical_ai": {
            "name": "피지컬 AI",
            "include": {
                "physical", "physical ai", "embodied", "embodiment",
                "simulation", "sim-to-real", "sim2real", "domain randomization",
                "visual motor", "visuomotor", "tactile", "haptic",
                "dexterous", "dexterity", "motor control", "neural control"
            },
            "exclude": set()
        },
        
        "realworld": {
            "name": "리얼월드",
            "include": {
                "real world", "real-world", "realistic", "realistic simulation",
                "deployment", "in-the-wild", "outdoor", "indoor",
                "autonomous driving", "self-driving", "mobile robot",
                "service robot", "industrial robot", "field robot"
            },
            "exclude": set()
        },
        
        "vision": {
            "name": "컴퓨터 비전",
            "include": {
                "vision", "visual", "image", "video", "recognition",
                "detection", "segmentation", "tracking", "3d", "depth",
                "point cloud", "lidar", "camera", "rgbd"
            },
            "exclude": set()
        },
        
        "multimodal": {
            "name": "멀티모달",
            "include": {
                "multimodal", "vision-language", "vlm", "audio-visual",
                "cross-modal", "text-to-image", "text-to-video", "image-text",
                "vision language"
            },
            "exclude": set()
        },
        
        "vla": {
            "name": "VLA (Vision-Language-Action)",
            "include": {
                "vla", "vision language action", "vision-language-action",
                "vision language model", "vlm", "robot foundation model",
                "generalist robot", "robot policy", "general-purpose robot",
                "language-conditioned", "text-conditioned", "goal-conditioned",
                "rt-1", "rt-2", "rt-x", "openvla", "octo", "gr00t", "robocat",
                "bridge", "bridge dataset", "dobb-e", "aloha", "mobile aloha",
                "π0", "pi-zero", "physical intelligence", "figure", "1x",
                "lever arm", "act", "diffusion policy", "universalto"
            },
            "exclude": set()
        }
    }
    
    # 전체 필터 (로보틱스 + 피지컬 AI + 리얼월드 + VLA)
    ROBOTICS_PHYSICAL_REAL = {
        "name": "로보틱스 + 피지컬 AI + 리얼월드 + VLA",
        "include": {
            # 로보틱스
            "robot", "robotics", "manipulation", "grasping", "locomotion",
            "motion planning", "control", "autonomous", "drone", "uav",
            "manipulator", "bipedal", "quadruped", "humanoid", "actuator",
            # 피지컬 AI
            "physical", "physical ai", "embodied", "embodiment",
            "simulation", "sim-to-real", "sim2real", "domain randomization",
            "visuomotor", "tactile", "haptic", "dexterous", "dexterity",
            # 리얼월드
            "real world", "real-world", "realistic simulation", "deployment",
            "in-the-wild", "autonomous driving", "self-driving",
            "mobile robot", "service robot", "industrial robot",
            # VLA 관련
            "vla", "vision language action", "vision-language-action",
            "robot foundation model", "generalist robot", "robot policy",
            "language-conditioned", "goal-conditioned", "rt-1", "rt-2", "openvla",
            "octo", "gr00t", "robocat", "bridge", "dobb-e", "aloha", "pi-zero",
            "diffusion policy", "physical intelligence", "figure robot"
        },
        "exclude": {
            "purely theoretical", "only simulation", "no real robot"
        }
    }
    
    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
    
    def filter_papers(self, papers: List[Paper], min_score: float = 1.0) -> List[Paper]:
        """
        논문 필터링
        
        Args:
            papers: 필터링할 논문 리스트
            min_score: 최소 매칭 점수 (0~1)
            
        Returns:
            필터링된 논문 리스트
        """
        filtered = []
        
        for paper in papers:
            score = self._calculate_match_score(paper)
            if score >= min_score:
                filtered.append(paper)
        
        # 업보트 순으로 정렬
        filtered.sort(key=lambda p: p.upvotes, reverse=True)
        
        return filtered
    
    def _calculate_match_score(self, paper: Paper) -> float:
        """논문의 매칭 점수 계산 (0~1)"""
        if not self.config.include_keywords:
            # Preset 사용 시
            preset = self.ROBOTICS_PHYSICAL_REAL
            include_keywords = preset["include"]
            exclude_keywords = preset["exclude"]
        else:
            include_keywords = self.config.include_keywords
            exclude_keywords = self.config.exclude_keywords
        
        # 텍스트 결합
        text = self._get_combined_text(paper).lower()
        
        # 제외 키워드 체크
        for keyword in exclude_keywords:
            if keyword.lower() in text:
                return 0.0
        
        # 포함 키워드 매칭
        match_count = 0
        total_count = len(include_keywords)
        
        for keyword in include_keywords:
            if keyword.lower() in text:
                match_count += 1
        
        if total_count == 0:
            return 0.0
        
        return match_count / min(total_count, 10)  # 최대 10개 키워드만 카운트
    
    def _get_combined_text(self, paper: Paper) -> str:
        """논문의 모든 텍스트 결합"""
        parts = [
            paper.title,
            paper.summary,
            ", ".join(paper.authors),
            paper.organization or ""
        ]
        return " ".join(parts)
    
    def get_match_details(self, paper: Paper) -> dict:
        """매칭 상세 정보 반환"""
        if not self.config.include_keywords:
            preset = self.ROBOTICS_PHYSICAL_REAL
            include_keywords = preset["include"]
        else:
            include_keywords = self.config.include_keywords
        
        text = self._get_combined_text(paper).lower()
        
        matched = []
        for keyword in include_keywords:
            if keyword.lower() in text:
                matched.append(keyword)
        
        score = len(matched) / min(len(include_keywords), 10)
        
        return {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "matched_keywords": matched,
            "match_count": len(matched),
            "score": score
        }


def filter_robotics_papers(papers: List[Paper], preset_name: str = "robotics_physical_real") -> List[Paper]:
    """로보틱스 + 피지컬 AI + 리얼월드 관련 논문 필터링"""
    filter_obj = PaperFilter()
    
    if preset_name == "robotics_physical_real":
        preset = PaperFilter.ROBOTICS_PHYSICAL_REAL
    else:
        preset = PaperFilter.PRESETS.get(preset_name, PaperFilter.PRESETS["robotics"])
    
    # 임시 설정
    config = FilterConfig(
        include_keywords=preset["include"],
        exclude_keywords=preset["exclude"]
    )
    filter_obj.config = config
    
    return filter_obj.filter_papers(papers)


# 테스트
if __name__ == "__main__":
    from crawler import HuggingFacePapersCrawler
    
    print("🤖 로보틱스/피지컬AI/리얼월드/VLA 논문 필터링 테스트")
    print("=" * 60)
    
    # 논문 가져오기
    crawler = HuggingFacePapersCrawler()
    papers = crawler.fetch_daily_papers()
    
    if papers:
        # 필터링
        filtered = filter_robotics_papers(papers)
        
        print(f"\n📊 결과: {len(filtered)}/{len(papers)}개의 논문이 필터링됨")
        
        if filtered:
            print("\n🎯 필터링된 논문:")
            for i, paper in enumerate(filtered[:10], 1):
                print(f"\n{i}. {paper.title}")
                print(f"   ⬆️ {paper.upvotes} upvotes")
                print(f"   🔗 {paper.url}")
                
                # 매칭 상세
                filter_obj = PaperFilter()
                details = filter_obj.get_match_details(paper)
                if details["matched_keywords"]:
                    print(f"   🏷️ 매칭 키워드: {', '.join(details['matched_keywords'][:5])}")
    
    crawler.close()
